# 第三方元件授權聲明(Third-Party Notices)

local-dictate 本體採 MIT(見 [LICENSE](LICENSE))。安裝檔(`setup.exe`)與 portable 版**打包了下列第三方元件**,各依其原授權散布;各授權原文收錄在 [`licenses/`](licenses/) 目錄(隨安裝檔一併安裝)。

> 本檔對應 CI 乾淨環境的實際打包內容(`build-release.yml`,不含 nvidia-* 套件——GPU 加速是安裝後使用者自行 `pip install`,授權由使用者與 NVIDIA 之間成立)。

## Python 套件

| 元件 | 版本 | 授權 | 原文 |
|---|---|---|---|
| faster-whisper | 1.2.1 | MIT | `licenses/faster-whisper-1.2.1-LICENSE` |
| CTranslate2 | 4.8.0 | MIT | [上游 LICENSE](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE)(wheel 未附檔) |
| pynput | 1.8.2 | **LGPL-3.0** | `licenses/pynput-1.8.2-COPYING.LGPL`＋`licenses/LGPL-3.0.txt`＋`licenses/GPL-3.0.txt`;替換方式見 [LGPL-COMPLIANCE.md](LGPL-COMPLIANCE.md) |
| sounddevice | 0.5.5 | MIT | `licenses/sounddevice-0.5.5-LICENSE` |
| pyperclip | 1.11.0 | BSD-3-Clause | `licenses/pyperclip-1.11.0-LICENSE.txt` |
| numpy | 2.4.6 | BSD-3-Clause | `licenses/numpy-2.4.6-LICENSE.txt` |
| opencc-python-reimplemented | 0.1.7 | Apache-2.0 | `licenses/opencc-python-reimplemented-0.1.7-NOTICE.txt` |
| requests | 2.34.2 | Apache-2.0 | `licenses/requests-2.34.2-LICENSE` |
| huggingface_hub | 1.20.1 | Apache-2.0 | `licenses/huggingface_hub-1.20.1-LICENSE` |
| tokenizers | 0.23.1 | Apache-2.0 | [上游 LICENSE](https://github.com/huggingface/tokenizers/blob/main/LICENSE)(wheel 未附檔) |
| hf_xet | 1.5.1 | Apache-2.0 | `licenses/hf_xet-1.5.1-LICENSE` |
| PyAV(av) | 17.1.0 | BSD-3-Clause | `licenses/av-17.1.0-LICENSE.txt`;內含 FFmpeg,見下節 |
| onnxruntime | 1.27.0 | MIT | `licenses/onnxruntime-1.27.0-LICENSE` |
| certifi | 2026.4.22 | MPL-2.0 | `licenses/certifi-2026.4.22-LICENSE` |
| charset_normalizer | 3.4.7 | MIT | `licenses/charset_normalizer-3.4.7-LICENSE` |
| idna | 3.15 | BSD-3-Clause | `licenses/idna-3.15-LICENSE.md` |
| urllib3 | 2.7.0 | MIT | `licenses/urllib3-2.7.0-LICENSE.txt` |
| tqdm | 4.67.3 | MPL-2.0 AND MIT | [上游 LICENCE](https://github.com/tqdm/tqdm/blob/master/LICENCE)(wheel 未附檔) |

## 原生函式庫(隨上列 wheel 進入安裝檔)

| 元件 | 位置 | 授權 | 說明 |
|---|---|---|---|
| **FFmpeg**(avcodec/avformat/avutil/avfilter/avdevice) | `_internal/av.libs/` | **LGPL-2.1+** | PyAV 官方 wheel 之 LGPL 組態 build(**不含** x264/x265 等 GPL 元件)。原文:`licenses/LGPL-2.1.txt`;原始碼:<https://ffmpeg.org>、build 腳本:<https://github.com/PyAV-Org/pyav-ffmpeg>;替換方式見 [LGPL-COMPLIANCE.md](LGPL-COMPLIANCE.md) |
| dav1d | `_internal/av.libs/` | BSD-2-Clause | AV1 解碼器,<https://code.videolan.org/videolan/dav1d> |
| SVT-AV1 | `_internal/av.libs/` | BSD-3-Clause-Clear(含 AOM 專利授權) | <https://gitlab.com/AOMediaCodec/SVT-AV1> |
| PortAudio | `_internal/_sounddevice_data/` | MIT 式授權 | <http://www.portaudio.com/license.html> |
| OpenSSL 3(libcrypto) | `_internal/` | Apache-2.0 | <https://www.openssl.org/source/license.html> |
| Microsoft VC++ Runtime(msvcp 等) | `_internal/` | Microsoft 允許隨應用程式再散布之執行階段元件 | — |

## 模型與資料

| 元件 | 授權 | 說明 |
|---|---|---|
| Whisper(架構與權重,OpenAI) | MIT | <https://github.com/openai/whisper> |
| Systran/faster-whisper-base(安裝檔內建之 CTranslate2 轉換版權重) | MIT | <https://huggingface.co/Systran/faster-whisper-base> |
| Silero VAD(faster-whisper 內附 onnx 資產) | MIT | <https://github.com/snakers4/silero-vad> |
| OpenCC 簡繁轉換辭典資料 | Apache-2.0 | <https://github.com/BYVoid/OpenCC> |

## 執行環境

| 元件 | 授權 | 說明 |
|---|---|---|
| CPython 3.11(runtime、標準函式庫、tkinter) | PSF-2.0 | <https://docs.python.org/3/license.html> |
| Tcl/Tk(tkinter 底層) | BSD 式授權 | <https://www.tcl.tk/software/tcltk/license.html> |
| PyInstaller bootloader | GPL-2.0 **含例外條款**(允許任何授權之程式打包散布,不影響本專案 MIT) | <https://pyinstaller.org/en/stable/license.html> |

---

若發現任何元件之聲明缺漏或錯誤,請開 issue,我會補正。
