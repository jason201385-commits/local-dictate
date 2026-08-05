# 第三方元件授權聲明(Third-Party Notices)

local-dictate 本體採 MIT(見 [LICENSE](LICENSE))。安裝檔(`setup.exe`)與免安裝版(`portable.zip`)**都打包了下列第三方元件**,各依其原授權散布;各授權原文收錄在 [`licenses/`](licenses/) 目錄,**兩種散布形式都會附上**(v0.1.4 起;v0.1.3 的 portable 版漏了,見 [CHANGELOG](CHANGELOG.md))。

> 本檔對應 CI 乾淨環境的實際打包內容(`build-release.yml`,不含 nvidia-* 套件——GPU 加速是安裝後使用者自行 `pip install`,授權由使用者與 NVIDIA 之間成立)。

## Python 套件

> ⚠️ 下面這張表**由 `build/gen_notices.py` 從實際安裝環境自動產生**,每次 release 建置時重新產出,所以版本號一定對得上那一版真正打包的東西。不要手改。
>
> 為什麼要自動化:v0.1.3 手工維護時同時出了兩種錯——漏掉相依進來的 `click`,以及版本號寫成開發機的 `tqdm 4.67.3`(CI 實際裝的是 `4.70.0`)。兩種錯都不會有任何徵兆。
>
> `pynput` 是 **LGPL-3.0**,除表列原文外另附 `licenses/LGPL-3.0.txt` 與 `licenses/GPL-3.0.txt`,替換方式見 [LGPL-COMPLIANCE.md](LGPL-COMPLIANCE.md)。`av`(PyAV)的 wheel 內含 FFmpeg,見下一節。

<!-- BEGIN AUTOGEN:PYTHON-PACKAGES -->

<!-- 這張表由 build/gen_notices.py 從實際安裝環境產生,共 40 個套件。不要手改。 -->

| 元件 | 版本 | 授權 | 原文 |
|---|---|---|---|
| annotated-doc | 0.0.4 | MIT | `licenses/annotated-doc-0.0.4-LICENSE` |
| anyio | 4.13.0 | MIT | `licenses/anyio-4.13.0-LICENSE` |
| av | 17.1.0 | BSD-3-Clause | `licenses/av-17.1.0-LICENSE.txt` |
| certifi | 2026.4.22 | Mozilla Public License 2.0 (MPL 2.0) | `licenses/certifi-2026.4.22-LICENSE` |
| cffi | 2.0.0 | MIT | `licenses/cffi-2.0.0-LICENSE` |
| charset-normalizer | 3.4.7 | MIT | `licenses/charset-normalizer-3.4.7-LICENSE` |
| click | 8.4.1 | BSD-3-Clause | `licenses/click-8.4.1-LICENSE.txt` |
| colorama | 0.4.6 | BSD License | `licenses/colorama-0.4.6-LICENSE.txt` |
| ctranslate2 | 4.8.0 | MIT | [上游 LICENSE](https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE)(wheel 未附檔) |
| faster-whisper | 1.2.1 | MIT License | `licenses/faster-whisper-1.2.1-LICENSE` |
| filelock | 3.29.0 | MIT | `licenses/filelock-3.29.0-LICENSE` |
| flatbuffers | 25.12.19 | Apache Software License | wheel 未附檔,見上游 repo |
| fsspec | 2026.4.0 | BSD-3-Clause | `licenses/fsspec-2026.4.0-LICENSE` |
| h11 | 0.16.0 | MIT License | `licenses/h11-0.16.0-LICENSE.txt` |
| hf-xet | 1.5.1 | Apache-2.0 | `licenses/hf-xet-1.5.1-LICENSE` |
| httpcore | 1.0.9 | BSD-3-Clause | `licenses/httpcore-1.0.9-LICENSE.md` |
| httpx | 0.28.1 | BSD License | `licenses/httpx-0.28.1-LICENSE.md` |
| huggingface_hub | 1.20.1 | Apache Software License | `licenses/huggingface_hub-1.20.1-LICENSE` |
| idna | 3.15 | BSD-3-Clause | `licenses/idna-3.15-LICENSE.md` |
| markdown-it-py | 4.2.0 | MIT License | `licenses/markdown-it-py-4.2.0-LICENSE` |
| mdurl | 0.1.2 | MIT License | `licenses/mdurl-0.1.2-LICENSE` |
| numpy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | `licenses/numpy-2.4.6-LICENSE.txt` |
| onnxruntime | 1.27.0 | MIT License | `licenses/onnxruntime-1.27.0-LICENSE` |
| opencc-python-reimplemented | 0.1.7 | Apache Software License | `licenses/opencc-python-reimplemented-0.1.7-NOTICE.txt` |
| protobuf | 6.33.6 | 3-Clause BSD License | `licenses/protobuf-6.33.6-LICENSE` |
| pycparser | 3.0 | BSD-3-Clause | `licenses/pycparser-3.0-LICENSE` |
| Pygments | 2.20.0 | BSD-2-Clause | `licenses/Pygments-2.20.0-LICENSE` |
| pynput | 1.8.2 | GNU Lesser General Public License v3 (LGPLv3) | `licenses/pynput-1.8.2-COPYING.LGPL` |
| pyperclip | 1.11.0 | BSD License | `licenses/pyperclip-1.11.0-LICENSE.txt` |
| PyYAML | 6.0.3 | MIT License | `licenses/PyYAML-6.0.3-LICENSE` |
| requests | 2.34.2 | Apache Software License | `licenses/requests-2.34.2-LICENSE` |
| rich | 15.0.0 | MIT License | `licenses/rich-15.0.0-LICENSE` |
| shellingham | 1.5.4 | ISC License (ISCL) | `licenses/shellingham-1.5.4-LICENSE` |
| six | 1.17.0 | MIT License | `licenses/six-1.17.0-LICENSE` |
| sounddevice | 0.5.5 | MIT | `licenses/sounddevice-0.5.5-LICENSE` |
| tokenizers | 0.23.1 | Apache Software License | [上游 LICENSE](https://github.com/huggingface/tokenizers/blob/main/LICENSE)(wheel 未附檔) |
| tqdm | 4.67.3 | MPL-2.0 AND MIT | [上游 LICENSE](https://github.com/tqdm/tqdm/blob/master/LICENCE)(wheel 未附檔) |
| typer | 0.25.1 | MIT | `licenses/typer-0.25.1-LICENSE` |
| typing_extensions | 4.15.0 | PSF-2.0 | `licenses/typing_extensions-4.15.0-LICENSE` |
| urllib3 | 2.7.0 | MIT | `licenses/urllib3-2.7.0-LICENSE.txt` |

<!-- END AUTOGEN:PYTHON-PACKAGES -->

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
