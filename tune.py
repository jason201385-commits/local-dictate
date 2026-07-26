# -*- coding: utf-8 -*-
"""硬體剖析 + 實測調校 — 讓程式自己量你的電腦，而不是叫你猜。

用法：
    python tune.py            # 剖析硬體 → 給建議設定（快，不下載模型）
    python tune.py --bench    # 再多做一步：在你這台實際跑基準測試，用真數字決定
    python tune.py --apply    # 把建議直接寫進 config.json（會先問你）

為什麼需要這支：
「有沒有顯卡」不是二分法。VRAM 決定塞得下多大的模型、CPU 核心數決定沒有顯卡時
有多痛。同一份預設值放到不同機器上，有人 1 秒、有人 15 秒。與其寫一堆但書，
不如讓它自己量。
"""
import argparse
import ctypes
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CFG_PATH = HERE / "config.json"

# 一句話：候選模型由小到大。int8/int8_float16 是為了在小 VRAM 上塞得下。
LADDER = ["base", "small", "medium", "large-v3"]
TARGET_SEC = 2.5      # 一段 ~10 秒的話，轉寫超過這個秒數就開始有等待感


# ── 硬體剖析 ────────────────────────────────────────────────────────────
class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"


def ram_gb():
    try:
        if IS_WIN:
            m = MEMORYSTATUSEX()
            m.dwLength = ctypes.sizeof(m)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.ullTotalPhys / (1024 ** 3)
        if IS_MAC:
            out = subprocess.run(["sysctl", "-n", "hw.memsize"],
                                 capture_output=True, text=True, timeout=8)
            return int(out.stdout.strip()) / (1024 ** 3)
        with open("/proc/meminfo") as f:                      # Linux
            for line in f:
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) / (1024 ** 2)
    except Exception:
        pass
    return 0.0


def mac_chip():
    """回傳 (晶片名稱, 是否 Apple Silicon)。"""
    try:
        out = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                             capture_output=True, text=True, timeout=8)
        name = out.stdout.strip()
        return name, name.startswith("Apple")
    except Exception:
        return "?", False


def gpus():
    """問 nvidia-smi。沒裝驅動或沒有 NVIDIA 卡就回空清單。"""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=12)
        if out.returncode != 0:
            return []
        found = []
        for line in out.stdout.strip().splitlines():
            if "," in line:
                name, mem = line.rsplit(",", 1)
                found.append((name.strip(), int(mem.strip())))     # MiB
        return found
    except Exception:
        return []


def cuda_libs():
    lib = Path(os.__file__).parent / "site-packages" / "nvidia"
    return [p.parent.name for p in lib.glob("*/bin")] if lib.exists() else []


def profile():
    p = {
        "os": sys.platform,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "cores": os.cpu_count() or 0,
        "ram_gb": ram_gb(),
        "gpus": gpus(),
        "cuda_libs": cuda_libs(),
        "free_gb": shutil.disk_usage(Path.home()).free / (1024 ** 3),
    }
    p["vram_mb"] = max((m for _, m in p["gpus"]), default=0)
    p["gpu_ready"] = bool(p["gpus"] and p["cuda_libs"])
    p["chip"], p["apple_silicon"] = mac_chip() if IS_MAC else ("", False)
    return p


OS_NAME = {"win32": "Windows", "darwin": "macOS", "linux": "Linux"}


def print_profile(p):
    print("=" * 64)
    print("  你這台電腦")
    print("=" * 64)
    print(f"  作業系統   {OS_NAME.get(p['os'], p['os'])}")
    print(f"  Python     {p['python']}")
    if p["chip"]:
        print(f"  處理器     {p['chip']}")
    print(f"  CPU 核心   {p['cores']}（邏輯核心）")
    print(f"  記憶體     {p['ram_gb']:.1f} GB")
    print(f"  磁碟可用   {p['free_gb']:.1f} GB")
    if p["gpus"]:
        for name, mem in p["gpus"]:
            print(f"  顯示卡     {name}（VRAM {mem} MB）")
        if not p["cuda_libs"]:
            print("             ⚠️ 有 NVIDIA 卡但缺 CUDA 套件 → 現在會用 CPU")
            print("             補上：pip install nvidia-cublas-cu12 nvidia-cudnn-cu12 "
                  "nvidia-cuda-nvrtc-cu12")
    elif IS_MAC:
        print("  加速       ⚠️ CTranslate2（faster-whisper 的引擎）目前沒有 Apple GPU 後端，")
        print("             Mac 上是純 CPU 跑。Apple Silicon 的 CPU 夠快，small 通常可用；")
        print("             想吃 GPU 要換引擎（mlx-whisper / whisper.cpp Metal）")
        print("             ⚠️ 以上尚未在 Mac 實機驗證，請回報實際數字")
    else:
        print("  顯示卡     沒有可用的 NVIDIA GPU → 走 CPU")

    if not IS_WIN:
        print()
        print("  " + "─" * 60)
        print("  ⚠️ 轉寫核心（錄音、辨識、剪貼簿）是跨平台的，這支剖析工具也能跑，")
        print("     但『口述引擎』本體目前只有 Windows 版：全域熱鍵、目標視窗判斷、")
        print("     焦點還原、不搶焦點的小面板，全部是 Win32 API。")
        print("     移植對照表看 docs/macos.md，歡迎 PR。")
        print("  " + "─" * 60)


# ── 規則式建議（不下載模型，秒出）────────────────────────────────────────
def recommend(p):
    """回傳 (設定 dict, 理由字串)。門檻偏保守，實跑 --bench 才是真答案。"""
    if p["gpu_ready"]:
        v = p["vram_mb"]
        if v >= 6000:
            return ({"model": "large-v3", "beam_size": 1, "compute_type": "int8_float16"},
                    f"VRAM {v}MB 塞得下 large-v3。beam 1 是為了把延遲壓回 2 秒內，"
                    "難字（英文品牌名、專有名詞）比 medium 穩。")
        if v >= 4000:
            return ({"model": "medium", "beam_size": 5, "compute_type": "int8_float16"},
                    f"VRAM {v}MB 跑 medium 剛好。beam 5 不要降到 1，"
                    "省下的時間有限但英文名詞會聽錯。")
        return ({"model": "small", "beam_size": 5, "compute_type": "int8_float16"},
                f"VRAM {v}MB 偏小，medium 可能塞不下或要跟其他程式搶。先用 small。")
    if IS_MAC:
        c = p["cores"]
        if p["apple_silicon"] and c >= 10:
            return ({"model": "medium", "beam_size": 5, "compute_type": "int8"},
                    f"{p['chip']}／{c} 核心：Apple Silicon 的 CPU 夠快，medium 值得先試。"
                    "⚠️ 尚未在 Mac 實機驗證，請用 --bench 量你自己的數字。")
        if p["apple_silicon"]:
            return ({"model": "small", "beam_size": 5, "compute_type": "int8"},
                    f"{p['chip']}／{c} 核心：先用 small。⚠️ 待 Mac 實機驗證，"
                    "請用 --bench 量。")
        return ({"model": "small", "beam_size": 5, "compute_type": "int8"},
                f"Intel Mac／{c} 核心：沒有 GPU 加速，先用 small。"
                "⚠️ 待實機驗證，請用 --bench 量。")
    # 沒有 GPU：核心數決定痛感
    c = p["cores"]
    if c >= 16:
        return ({"model": "medium", "beam_size": 5, "compute_type": "int8"},
                f"{c} 核心的 CPU 跑 medium 還可以接受，但會有等待感。"
                "覺得慢就降到 small。")
    if c >= 8:
        return ({"model": "small", "beam_size": 5, "compute_type": "int8"},
                f"{c} 核心：small 是速度與準度的折衷。中文句子沒問題，"
                "英文專有名詞靠 vocab.txt 補。")
    return ({"model": "base", "beam_size": 1, "compute_type": "int8"},
            f"{c} 核心：只能用 base，辨識會明顯變差。"
            "強烈建議把常用詞寫進 vocab.txt，或考慮加一張 NVIDIA 顯卡。")


# ── 實測基準（--bench）──────────────────────────────────────────────────
SAMPLE_TEXT = "今天我把報價單改好了，然後把待辦清單整理了一遍，明天要處理維護的事情。"


def make_sample(dst):
    """做一段中文語音樣本當基準，不需要外掛音檔。
    Windows 用內建語音合成，macOS 用 say。"""
    if IS_MAC:
        try:
            aiff = str(Path(dst).with_suffix(".aiff"))
            subprocess.run(["say", "-v", "Meijia", "-o", aiff, SAMPLE_TEXT],
                           capture_output=True, timeout=90)
            if not Path(aiff).exists():      # 沒裝中文語音就用預設嗓音
                subprocess.run(["say", "-o", aiff, SAMPLE_TEXT],
                               capture_output=True, timeout=90)
            if Path(aiff).exists():
                subprocess.run(["ffmpeg", "-y", "-i", aiff, str(dst)],
                               capture_output=True, timeout=60)
                Path(aiff).unlink(missing_ok=True)
            return Path(dst).exists() and Path(dst).stat().st_size > 1000
        except Exception:
            return False
    if not IS_WIN:
        return False
    ps = (
        "Add-Type -AssemblyName System.Speech;"
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture -like 'zh*' } "
        "| Select-Object -First 1;"
        "if ($v) { $s.SelectVoice($v.VoiceInfo.Name) }"
        "$s.Rate = -1;"
        f"$s.SetOutputToWaveFile('{dst}');"
        f"$s.Speak('{SAMPLE_TEXT}');"
        "$s.Dispose();"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True, timeout=90)
    return Path(dst).exists() and Path(dst).stat().st_size > 1000


def load_wav(path, sr=16000):
    import wave
    import numpy as np
    tmp = Path(path).with_name("_bench16k.wav")
    subprocess.run(["ffmpeg", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sr), str(tmp)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(str(tmp), "rb") as w:
        raw = w.readframes(w.getnframes())
    tmp.unlink(missing_ok=True)
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0


def bench(p, models):
    import numpy as np
    from faster_whisper import WhisperModel

    sample = HERE / "_bench_sample.wav"
    audio = None
    if shutil.which("ffmpeg") and make_sample(str(sample)):
        try:
            audio = load_wav(sample)
            print(f"\n測試樣本：{len(audio)/16000:.1f} 秒中文語音（Windows 內建語音合成）")
        except Exception as e:
            print(f"（樣本轉檔失敗：{str(e)[:60]}）")
    sample.unlink(missing_ok=True)
    if audio is None:
        audio = (np.random.randn(16000 * 10) * 0.02).astype(np.float32)
        print("\n⚠️ 做不出語音樣本（缺 ffmpeg 或中文語音），改用雜訊只測速度、不看辨識結果")

    dev, ctype = ("cuda", "int8_float16") if p["gpu_ready"] else ("cpu", "int8")
    print(f"裝置：{dev}／{ctype}    目標：{TARGET_SEC} 秒內\n")
    rows = []
    for size in models:
        try:
            print(f"  {size:9s} 載入中…", end="", flush=True)
            t0 = time.time()
            m = WhisperModel(size, device=dev, compute_type=ctype)
            load = time.time() - t0
            m.transcribe(np.zeros(16000, dtype=np.float32), language="zh",
                         beam_size=1, vad_filter=False)
            best, txt = 1e9, ""
            for beam in (5, 1):
                t0 = time.time()
                segs, _ = m.transcribe(audio, language="zh", beam_size=beam,
                                       vad_filter=True,
                                       initial_prompt="以下是繁體中文的口述內容。")
                out = "".join(s.text for s in segs).strip()
                el = time.time() - t0
                rows.append((size, beam, el, out))
                if el < best:
                    best, txt = el, out
            del m
            print(f"\r  {size:9s} 載入 {load:4.1f}s   最快 {best:5.2f}s"
                  f"   {'✅' if best <= TARGET_SEC else '⚠️ 偏慢'}")
        except Exception as e:
            print(f"\r  {size:9s} ❌ {str(e)[:70]}")
    return rows


def pick_from_bench(rows):
    """在達標的組合裡挑最大的模型；都不達標就挑最快的。"""
    if not rows:
        return None
    ok = [r for r in rows if r[2] <= TARGET_SEC]
    pool = ok or rows
    rank = {m: i for i, m in enumerate(LADDER)}
    if ok:
        best = max(pool, key=lambda r: (rank.get(r[0], -1), -r[2]))
    else:
        best = min(pool, key=lambda r: r[2])
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", action="store_true", help="實際跑基準測試（會下載模型，較久）")
    ap.add_argument("--apply", action="store_true", help="把建議寫進 config.json")
    a = ap.parse_args()

    p = profile()
    print_profile(p)
    cfg, why = recommend(p)
    print("\n" + "=" * 64)
    print("  建議設定（依硬體推算）")
    print("=" * 64)
    for k, v in cfg.items():
        print(f"  {k:14s} {v}")
    print(f"\n  理由：{why}")

    if a.bench:
        # 只測建議值附近的三階，不要把五個模型全下載一遍
        i = LADDER.index(cfg["model"])
        models = LADDER[max(0, i - 1): i + 2]
        print("\n" + "=" * 64)
        print(f"  實測基準（{'、'.join(models)}）")
        print("=" * 64)
        print("  第一次跑會下載模型，請留時間與網路。")
        rows = bench(p, models)
        best = pick_from_bench(rows)
        if best:
            size, beam, el, txt = best
            cfg["model"], cfg["beam_size"] = size, beam
            print("\n  ── 實測結論 ──")
            print(f"  用 {size} + beam {beam}：{el:.2f} 秒"
                  f"{'（達標）' if el <= TARGET_SEC else '（這台機器最快也只能這樣）'}")
            if txt:
                print(f"  辨識結果：{txt}")
            print("\n  提醒：辨識結果如果把英文名詞聽錯，把那些詞寫進 vocab.txt，"
                  "\n        效果通常比換更大的模型明顯。")

    if a.apply:
        cur = {}
        if CFG_PATH.exists():
            cur = json.loads(CFG_PATH.read_text(encoding="utf-8-sig"))
        cur.update({k: v for k, v in cfg.items() if k != "compute_type"})
        CFG_PATH.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n✅ 已寫進 {CFG_PATH.name}（重開口述引擎生效）")
    else:
        print("\n（要套用就加 --apply；想用真實數字決定就加 --bench）")


if __name__ == "__main__":
    main()
