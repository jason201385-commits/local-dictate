# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包規格 — local-dictate

用法（在 repo 根目錄）：
    pip install pyinstaller
    pyinstaller build/local-dictate.spec --noconfirm

刻意的決定（每一條都有理由，改之前先讀）：
  · --onedir 不是 --onefile：onefile 每次啟動要解壓到暫存目錄，啟動變慢、
    防毒更容易誤判、崩潰時會留下 _MEI 殘骸、除錯困難。PyInstaller 官方也建議
    先讓 one-folder 正常再考慮 one-file。
  · console=False：使用者不該看到黑視窗。代價是啟動期的例外會沒有地方顯示，
    所以程式端已經把 sys.stdout/stderr 接住並全部寫進 dictate.log。
  · upx=False：UPX 壓縮原生 DLL 會明顯提高防毒誤判率，省下的體積不值得。
  · 不打包 CUDA：nvidia-* 套件裝完佔約 1.9GB（本機實測），而且是 proprietary
    授權，能不能重新散布要另外確認。GPU 加速留給安裝後選配。
    ⚠️ 但「CI 過濾 nvidia-*」只擋 pip 套件，**擋不掉別的 wheel 自己夾帶** ——
    ctranslate2 的 wheel 內建 cudnn64_9.dll，v0.1.3（含）以前它一直在產物裡，
    跟這段文字寫的相反。所以下面另外用 _drop_proprietary() 濾，並由 CI 斷言把關。
  · 不打包 av / FFmpeg：PyAV 的 Windows wheel 內含 libx264/libx265（GPL-2.0+），
    而即時聽寫用不到（音訊是 numpy array 直接進模型）。見 build/rthook_no_av.py。
  · 不打包模型：模型要能跟程式獨立更新，塞進 exe 會讓每次改版都重傳 1.5GB。

**通則（這份 spec 付出代價學到的）：宣稱要由產物驗證，不能由設定或訊息驗證。**
spec 印出「已排除」不代表東西真的不見了 —— 第一次修 cuDNN 時只濾了
collect_dynamic_libs，collect_data_files 又把同一顆 DLL 收回來，訊息照印。
所以 .github/workflows/build-release.yml 有對應的斷言直接掃產物檔名。
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

ROOT = os.path.abspath(os.path.join(os.getcwd()))


def _say(msg):
    """印 spec 的進度訊息，但不要因為編碼把整個 build 弄掛。

    ⚠️ 2026-07-30 CI 實際踩到：GitHub runner 的 stdout 預設是 cp1252，
    spec 裡的中文 print 直接噴 UnicodeEncodeError，PyInstaller 整個 exit 1。
    本機是中文 Windows 所以完全沒事 —— 又一次「本機能跑 ≠ CI 能跑」。
    CI 那邊另外設了 PYTHONIOENCODING=utf-8，這裡是第二層保險。
    """
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "backslashreplace").decode("ascii"))

# ── 原生資料與 DLL ──────────────────────────────────────────────────────
datas = []
binaries = []

# ctranslate2：faster-whisper 的推論引擎，.pyd 旁邊有一票 DLL
# ⚠️ 這個 wheel 內建 cudnn64_9.dll（NVIDIA 專有授權）。2026-07-30 合規審查抓到：
#    本專案到處寫「不打包 CUDA、不含 nvidia-*」，但那道防線只擋 pip 的 nvidia-* 套件，
#    擋不掉「別的 wheel 自己夾帶」——產物裡一直有它，宣稱與事實不符。
#    而且 CPU 推論根本用不到它（cuDNN 只在 device="cuda" 時載入），
#    GPU 加速是安裝後自行 `pip install nvidia-cudnn-cu12`，那個套件會提供自己的 cudnn。
#    所以這裡直接濾掉，少散布一個專有二進位。
#    ⚠️ 要濾**兩條路**：collect_dynamic_libs 抓 DLL，collect_data_files 也會把同一批 .dll
#       當資料檔再收一次。第一次只濾了前者，spec 照樣印出「已排除」，產物裡卻還是有它
#       ——訊息說做了、東西還在。所以下面用同一個 filter 套在兩邊，並由 CI 斷言把關。
def _drop_proprietary(entries):
    keep, dropped = [], []
    for src, dst in entries:
        (dropped if "cudnn" in os.path.basename(src).lower() else keep).append((src, dst))
    return keep, dropped


_ct2_libs, _d1 = _drop_proprietary(collect_dynamic_libs("ctranslate2"))
_ct2_datas, _d2 = _drop_proprietary(collect_data_files("ctranslate2"))
if _d1 or _d2:
    _say(f"[spec] 已排除 NVIDIA 專有 DLL："
         f"{sorted({os.path.basename(s) for s, _ in _d1 + _d2})}")
binaries += _ct2_libs
datas += _ct2_datas

# av / FFmpeg：**刻意不打包**。PyAV 的 Windows wheel 內含 libx264/libx265（GPL-2.0+），
# 而即時聽寫用不到它們（音訊是 numpy array 直接進模型，不走檔案解碼）。
# 詳細理由與證據見 build/rthook_no_av.py。
# 原本這裡是 `binaries += collect_dynamic_libs("av")` —— 那會把 25MB 的 GPL 編碼器
# 一起散布，並讓「本專案 MIT，拿去賣都可以」這句話對二進位版變成錯的。

# sounddevice 的 PortAudio DLL 放在獨立的 _sounddevice_data 套件裡
datas += collect_data_files("_sounddevice_data")

# OpenCC 的簡繁字典（純資料檔，漏了就會在轉換時炸掉）
datas += collect_data_files("opencc")

# faster-whisper 自帶的 assets（VAD 模型等）
datas += collect_data_files("faster_whisper")

# tokenizers 的原生模組
binaries += collect_dynamic_libs("tokenizers")

# HTTPS 憑證：整理層要打 API，沒有這個會 SSL 驗證失敗
datas += collect_data_files("certifi")

# 專案自己的檔案
for f in ("vocab.example.txt", "SKILL.md"):
    p = os.path.join(ROOT, f)
    if os.path.exists(p):
        datas.append((p, "."))

# 授權文件 —— 必須在 PyInstaller 產物裡,不能只靠 installer.iss。
# 為什麼(2026-07-30 實測踩到):portable zip 是 CI 直接壓 dist\local-dictate\*,
# 完全繞過 installer.iss。v0.1.3 因此出貨了一份「安裝檔有授權文、免安裝版沒有」
# 的東西 —— 而 portable zip 一樣是散布,MIT/BSD 要求保留聲明、LGPL 要求附全文。
# 放這裡 = 任何從 dist\ 出發的散布形式都自動合規。
for f in ("THIRD_PARTY_NOTICES.md", "LGPL-COMPLIANCE.md", "LICENSE"):
    p = os.path.join(ROOT, f)
    if os.path.exists(p):
        datas.append((p, "."))
_licenses = os.path.join(ROOT, "licenses")
if os.path.isdir(_licenses):
    for name in sorted(os.listdir(_licenses)):
        p = os.path.join(_licenses, name)
        if os.path.isfile(p):
            datas.append((p, "licenses"))

hiddenimports = [
    "ctranslate2",
    "faster_whisper",
    "sounddevice",
    "opencc",
    "pynput.keyboard._win32",
    "pynput.mouse._win32",
    "tkinter",
    "tkinter.ttk",
    "requests",
    "charset_normalizer",
    "certifi",
]

a = Analysis(
    [os.path.join(ROOT, "dictate.py")],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    # 啟動時把 av 換成 stub，讓 faster_whisper 的 `import av` 不會炸
    runtime_hooks=[os.path.join(ROOT, "build", "rthook_no_av.py")],
    # 明確排除用不到的大套件，不要讓它們被 pull 進來
    # "av" 是授權考量（GPL 的 x264/x265），不是體積考量 —— 見 build/rthook_no_av.py
    excludes=["matplotlib", "scipy", "pandas", "PIL", "PyQt5", "PySide6",
              "IPython", "notebook", "pytest", "torch", "torchvision",
              "av"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="local-dictate",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,               # ← 不要開，會提高防毒誤判
    console=False,           # ← 沒有黑視窗；錯誤全部寫 dictate.log
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="local-dictate",
)

# ── COLLECT 之後：把授權文件再複製一份到 exe 旁邊 ──────────────────────────
# 為什麼需要這一段（2026-07-30 本機實跑才發現）：
# PyInstaller 6 的 onedir 版面會把**所有** datas 塞進 _internal\，
# 所以上面那些 datas.append((p, ".")) 的落點其實是 _internal\，不是使用者看得到的地方。
# 授權文件埋在 _internal\ 裡雖然「有附」，但沒有人會去那裡找 ——
# MIT/BSD 要的是「隨散布提供聲明」，讓人找得到才有意義。
# COLLECT() 建構完成時產物已經寫到磁碟，所以這裡直接複製即可。
_dist = globals().get("DISTPATH")
if _dist:
    import shutil

    _out = os.path.join(_dist, "local-dictate")
    if os.path.isdir(_out):
        for f in ("THIRD_PARTY_NOTICES.md", "LGPL-COMPLIANCE.md", "LICENSE"):
            p = os.path.join(ROOT, f)
            if os.path.exists(p):
                shutil.copy2(p, os.path.join(_out, f))
        if os.path.isdir(_licenses):
            _dst = os.path.join(_out, "licenses")
            os.makedirs(_dst, exist_ok=True)
            for name in sorted(os.listdir(_licenses)):
                p = os.path.join(_licenses, name)
                if os.path.isfile(p):
                    shutil.copy2(p, os.path.join(_dst, name))
        _say("[spec] 已把授權文件複製到產物根目錄（exe 旁邊）")
