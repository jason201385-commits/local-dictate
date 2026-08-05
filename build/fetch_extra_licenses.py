#!/usr/bin/env python3
"""取得「不是 pip 套件」那些元件的授權原文,放進 licenses/。

`gen_notices.py` 只能從 wheel 的 dist-info 收割授權檔,但產物裡還有一批東西
拿不到 dist-info,或上游 wheel 根本沒附:

  · 原生函式庫:PortAudio(隨 sounddevice)、OpenSSL(隨 Python)
  · 執行環境:CPython、PyInstaller bootloader
  · wheel 沒附授權檔的套件:CTranslate2、tokenizers、flatbuffers
  · 模型與資料:Whisper 權重、Silero VAD

MIT / BSD / Apache / PSF 要求的是「散布時隨附授權**條文**」,不是「給一個連結」。
所以這些也必須有本地原文,不能只在 THIRD_PARTY_NOTICES.md 放 URL
(2026-07-30 合規審查抓到,v0.1.3 整節整節只有連結)。

這支腳本是**一次性/偶爾跑**的:抓下來的檔案會提交進版控,CI 不需要連外。
上游改版時再手動跑一次。

用法:
    python build/fetch_extra_licenses.py           # 缺的才抓
    python build/fetch_extra_licenses.py --force   # 全部重抓
"""
from __future__ import annotations

import argparse
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LICENSES = os.path.join(ROOT, "licenses")

# (輸出檔名, 來源 URL, 說明)
SOURCES = [
    ("portaudio-LICENSE.txt",
     "https://raw.githubusercontent.com/PortAudio/portaudio/master/LICENSE.txt",
     "PortAudio —— sounddevice 的錄音底層,DLL 在 _internal/_sounddevice_data/"),
    ("openssl-LICENSE.txt",
     "https://raw.githubusercontent.com/openssl/openssl/master/LICENSE.txt",
     "OpenSSL 3 —— libcrypto/libssl,隨 CPython 進到 _internal/"),
    ("cpython-LICENSE.txt",
     "https://raw.githubusercontent.com/python/cpython/3.11/LICENSE",
     "CPython 3.11 runtime 與標準函式庫(PSF-2.0)"),
    ("pyinstaller-COPYING.txt",
     "https://raw.githubusercontent.com/pyinstaller/pyinstaller/develop/COPYING.txt",
     "PyInstaller bootloader(GPL-2.0 含例外條款,不影響本專案 MIT)"),
    ("ctranslate2-LICENSE.txt",
     "https://raw.githubusercontent.com/OpenNMT/CTranslate2/master/LICENSE",
     "CTranslate2 —— faster-whisper 的推論引擎(wheel 未附授權檔)"),
    ("tokenizers-LICENSE.txt",
     "https://raw.githubusercontent.com/huggingface/tokenizers/main/LICENSE",
     "tokenizers(wheel 未附授權檔)"),
    ("flatbuffers-LICENSE.txt",
     "https://raw.githubusercontent.com/google/flatbuffers/master/LICENSE",
     "flatbuffers —— onnxruntime 相依(wheel 未附授權檔)"),
    ("whisper-LICENSE.txt",
     "https://raw.githubusercontent.com/openai/whisper/main/LICENSE",
     "Whisper 模型架構與權重(OpenAI, MIT);安裝檔內建的 Systran 轉換版同此授權"),
    ("silero-vad-LICENSE.txt",
     "https://raw.githubusercontent.com/snakers4/silero-vad/master/LICENSE",
     "Silero VAD —— faster-whisper 內附的 onnx 資產"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="已存在也重抓")
    args = ap.parse_args()

    os.makedirs(LICENSES, exist_ok=True)
    ok = fail = skip = 0
    for name, url, desc in SOURCES:
        dst = os.path.join(LICENSES, name)
        if os.path.exists(dst) and not args.force:
            print(f"  - {name}(已存在,略過)")
            skip += 1
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "local-dictate-license-fetch"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if len(data) < 200:
                raise ValueError(f"內容只有 {len(data)} bytes,不像授權原文")
            with open(dst, "wb") as f:
                f.write(data)
            print(f"  ✅ {name}  {len(data):,} bytes  — {desc}")
            ok += 1
        except Exception as e:
            print(f"  ❌ {name}:{e}\n     來源:{url}", file=sys.stderr)
            fail += 1

    print(f"\n新抓 {ok} 份、略過 {skip} 份、失敗 {fail} 份 → {LICENSES}")
    if fail:
        print("失敗的請手動下載後放進 licenses/,檔名要跟上面一致"
              "(gen_notices.py 的 KEEP_ALWAYS 靠檔名保護它們不被清掉)。", file=sys.stderr)
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
