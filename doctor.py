# -*- coding: utf-8 -*-
"""環境健檢 — 跑這支就知道你的機器還缺什麼。

用法：python doctor.py       （或雙擊 檢查環境.bat）

每一項都會給「現況 + 缺了怎麼補」，不會只丟一個錯誤訊息叫你自己查。
"""
import os
import shutil
import sys
from pathlib import Path

OK, WARN, BAD = "✅", "⚠️ ", "❌"
issues = []          # (嚴重度, 標題, 怎麼修)


def report(level, title, detail="", fix=""):
    print(f"{level} {title}")
    if detail:
        print(f"     {detail}")
    if level in (WARN, BAD) and fix:
        issues.append((level, title, fix))


print("=" * 62)
print("  local-dictate 環境健檢")
print("=" * 62)

# ── 1. 作業系統 ─────────────────────────────────────────────────────────
print("\n【系統】")
if sys.platform != "win32":
    report(BAD, f"作業系統 {sys.platform}", "本專案用到 Win32 API，目前只支援 Windows",
           "在 Windows 上執行；macOS / Linux 的移植歡迎 PR")
else:
    report(OK, "Windows")

v = sys.version_info
if v < (3, 10):
    report(BAD, f"Python {v.major}.{v.minor}.{v.micro}", "需要 3.10 以上",
           "到 https://www.python.org/downloads/ 裝新版，安裝時勾「Add python.exe to PATH」")
else:
    report(OK, f"Python {v.major}.{v.minor}.{v.micro}")

# ── 2. 套件 ─────────────────────────────────────────────────────────────
print("\n【套件】")
NEEDED = [
    ("faster_whisper", "faster-whisper", True, "語音辨識核心"),
    ("sounddevice", "sounddevice", True, "麥克風錄音"),
    ("pynput", "pynput", True, "全域熱鍵 + 模擬貼上"),
    ("pyperclip", "pyperclip", True, "剪貼簿"),
    ("numpy", "numpy", True, "音訊處理"),
    ("opencc", "opencc-python-reimplemented", False, "簡體→繁體轉換"),
    ("requests", "requests", False, "「整理」功能才會用到"),
]
for mod, pkg, required, what in NEEDED:
    try:
        m = __import__(mod)
        ver = getattr(m, "__version__", "")
        report(OK, f"{pkg} {ver}".strip())
    except Exception:
        report(BAD if required else WARN, f"{pkg} 沒裝（{what}）", "",
               f"pip install {pkg}")

try:
    import tkinter  # noqa: F401
    report(OK, "tkinter（小面板）")
except Exception:
    report(WARN, "tkinter 沒有", "會退回「只有熱鍵、沒有小面板」模式",
           "多數 python.org 版本內建；用 conda 的話：conda install tk")

# ── 3. GPU ──────────────────────────────────────────────────────────────
print("\n【運算裝置】")
lib = Path(os.__file__).parent / "site-packages" / "nvidia"
cuda_dirs = [p for p in lib.glob("*/bin") if p.is_dir()] if lib.exists() else []
for b in cuda_dirs:
    os.environ["PATH"] = str(b) + os.pathsep + os.environ["PATH"]
    try:
        os.add_dll_directory(str(b))
    except Exception:
        pass

gpu_ok = False
if cuda_dirs:
    try:
        from faster_whisper import WhisperModel
        WhisperModel("tiny", device="cuda", compute_type="int8_float16")
        gpu_ok = True
        report(OK, "GPU（CUDA）可用", "轉寫約 1 秒等級")
    except Exception as e:
        report(WARN, "有 CUDA 套件但載不起來", str(e)[:90],
               "通常是顯卡驅動太舊 → 更新 NVIDIA 驅動程式；不修也能跑，只是走 CPU")
else:
    report(WARN, "沒有 CUDA 套件 → 會用 CPU",
           f"CPU 邏輯核心 {os.cpu_count()}。22 核實測：medium 6.7s／small 3.3s／base 1.2s（11 秒音檔）",
           "有 NVIDIA 顯卡：pip install nvidia-cublas-cu12 nvidia-cudnn-cu12 nvidia-cuda-nvrtc-cu12\n"
           "        沒有顯卡：把 config.json 的 model 改成 small（速度與準度的折衷）")

# ── 4. 麥克風 ───────────────────────────────────────────────────────────
print("\n【麥克風】")
try:
    import winreg
    key = (r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager"
           r"\ConsentStore\microphone")
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key) as k:
        val = winreg.QueryValueEx(k, "Value")[0]
    if str(val).lower() == "allow":
        report(OK, "Windows 麥克風權限：允許")
    else:
        report(BAD, f"Windows 麥克風權限：{val}", "系統層被關掉了，程式一定收不到聲音",
               "設定 → 隱私權與安全性 → 麥克風 → 開啟，並確認「讓桌面應用程式存取您的麥克風」也是開的")
except Exception:
    report(WARN, "讀不到麥克風權限設定", "不一定有問題，但錄不到聲音時先去這裡看",
           "設定 → 隱私權與安全性 → 麥克風")

try:
    import sounddevice as sd
    ins = [(i, d["name"]) for i, d in enumerate(sd.query_devices())
           if d["max_input_channels"] > 0]
    if not ins:
        report(BAD, "找不到任何輸入裝置", "", "插上麥克風，或到音效設定啟用內建麥克風")
    else:
        default = sd.query_devices(sd.default.device[0])["name"]
        report(OK, f"預設輸入裝置：{default}", f"另外還有 {len(ins) - 1} 個可選")
        import numpy as np
        rec = sd.rec(int(0.7 * 16000), samplerate=16000, channels=1, dtype="float32")
        sd.wait()
        rms = float(np.sqrt((rec ** 2).mean()))
        if rms < 0.00002:
            report(WARN, f"試錄 0.7 秒，音量幾乎是 0（RMS {rms:.6f}）",
                   "安靜環境本來就會很小，但如果你剛剛有講話就是不正常",
                   "確認裝置沒被靜音、沒被其他程式獨佔（會議軟體最常見）")
        else:
            report(OK, f"試錄成功（RMS {rms:.5f}）")
except Exception as e:
    report(BAD, "開麥克風失敗", str(e)[:90], "檢查上面的權限設定與裝置")

# ── 5. 模型與空間 ───────────────────────────────────────────────────────
print("\n【模型與磁碟】")
hub = Path.home() / ".cache" / "huggingface" / "hub"
cached = sorted({p.name.replace("models--Systran--faster-whisper-", "")
                 for p in hub.glob("models--*faster-whisper*")}) if hub.exists() else []
if cached:
    report(OK, "已下載的模型：" + "、".join(cached))
else:
    report(WARN, "還沒下載任何模型", "第一次啟動會自動下載（medium 約 1.5GB），需要網路且要等一下",
           "不用手動處理，但第一次跑請留時間；之後就離線可用")

free = shutil.disk_usage(Path.home()).free / (1024 ** 3)
if free < 3:
    report(BAD, f"家目錄所在磁碟剩 {free:.1f} GB", "模型放這裡，空間不夠會下載失敗",
           "清出至少 3GB")
else:
    report(OK, f"磁碟可用空間 {free:.1f} GB")

# ── 6. 選配 ─────────────────────────────────────────────────────────────
print("\n【選配】")
if os.environ.get("NVIDIA_API_KEY"):
    report(OK, "NVIDIA_API_KEY 已設定", "「✨整理」功能可用")
else:
    report(WARN, "沒有 NVIDIA_API_KEY", "「✨整理」會自動退回貼原文——不會壞，只是不幫你去口頭禪",
           "到 https://build.nvidia.com/ 申請免費 key，設成環境變數 NVIDIA_API_KEY；\n"
           "        或改 config.json 的 polish.url / polish.model 換成別家 OpenAI 相容 API；\n"
           "        或直接把 polish.enabled 設 false，全程離線")

if shutil.which("ffmpeg"):
    report(OK, "ffmpeg 有裝", "只有 --file 自我測試用得到，日常聽寫不需要")
else:
    report(WARN, "沒有 ffmpeg", "日常聽寫不影響；只有 `python dictate.py --file 音檔` 會用到",
           "要用的話：winget install Gyan.FFmpeg")

here = Path(__file__).resolve().parent
try:
    t = here / ".write_test"
    t.write_text("x", encoding="utf-8")
    t.unlink()
    report(OK, "專案資料夾可寫入", "config.json / vocab.txt / dictate.log 會放這裡")
except Exception as e:
    report(BAD, "專案資料夾不能寫", str(e)[:80],
           "把整個資料夾移到你的使用者目錄底下，不要放在 Program Files")

# ── 總結 ────────────────────────────────────────────────────────────────
print("\n" + "=" * 62)
blockers = [i for i in issues if i[0] == BAD]
if not issues:
    print("  全部通過，直接啟動就能用。")
elif not blockers:
    print(f"  可以跑，但有 {len(issues)} 個地方值得處理：")
else:
    print(f"  有 {len(blockers)} 個問題會讓它不能用：")
print("=" * 62)
for level, title, fix in issues:
    print(f"\n{level} {title}\n     → {fix}")
print()
sys.exit(1 if blockers else 0)
