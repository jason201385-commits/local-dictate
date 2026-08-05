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
  · 不打包模型：模型要能跟程式獨立更新，塞進 exe 會讓每次改版都重傳 1.5GB。
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

ROOT = os.path.abspath(os.path.join(os.getcwd()))

# ── 原生資料與 DLL ──────────────────────────────────────────────────────
datas = []
binaries = []

# ctranslate2：faster-whisper 的推論引擎，.pyd 旁邊有一票 DLL
binaries += collect_dynamic_libs("ctranslate2")
datas += collect_data_files("ctranslate2")

# av / FFmpeg：faster-whisper 用它解音訊
binaries += collect_dynamic_libs("av")

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
    runtime_hooks=[],
    # 明確排除用不到的大套件，不要讓它們被 pull 進來
    excludes=["matplotlib", "scipy", "pandas", "PIL", "PyQt5", "PySide6",
              "IPython", "notebook", "pytest", "torch", "torchvision"],
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
        print("[spec] 已把授權文件複製到產物根目錄（exe 旁邊）")
