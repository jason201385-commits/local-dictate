# 第三方元件授權聲明(Third-Party Notices)

local-dictate 本體採 MIT(見 [LICENSE](LICENSE))。安裝檔(`setup.exe`)與免安裝版(`portable.zip`)**都打包了下列第三方元件**,各依其原授權散布;各授權原文收錄在 [`licenses/`](licenses/) 目錄,**兩種散布形式都會附上**(v0.1.4 起;v0.1.3 的 portable 版漏了,見 [CHANGELOG](CHANGELOG.md))。

> 本檔對應 CI 乾淨環境的實際打包內容(`build-release.yml`,不含 nvidia-* 套件——GPU 加速是安裝後使用者自行 `pip install`,授權由使用者與 NVIDIA 之間成立)。

## Python 套件

> ⚠️ 下面這張表**由 `build/gen_notices.py` 從實際安裝環境自動產生**,每次 release 建置時重新產出,所以版本號一定對得上那一版真正打包的東西。不要手改。
>
> 為什麼要自動化:v0.1.3 手工維護時同時出了兩種錯——漏掉相依進來的 `click`,以及版本號寫成開發機的 `tqdm 4.67.3`(CI 實際裝的是 `4.70.0`)。兩種錯都不會有任何徵兆。
>
> `pynput` 是 **LGPL-3.0**,除表列原文外另附 `licenses/LGPL-3.0.txt` 與 `licenses/GPL-3.0.txt`,替換方式見 [LGPL-COMPLIANCE.md](LGPL-COMPLIANCE.md)。
>
> `av`(PyAV)**不在這張表裡**,因為 v0.1.4 起不再打包——理由見下方 FFmpeg 那一節。

<!-- BEGIN AUTOGEN:PYTHON-PACKAGES -->

<!-- 這張表由 build/gen_notices.py 從實際安裝環境產生,共 39 個套件。不要手改。 -->

| 元件 | 版本 | 授權 | 原文 |
|---|---|---|---|
| annotated-doc | 0.0.4 | MIT | `licenses/annotated-doc-0.0.4-LICENSE` |
| anyio | 4.13.0 | MIT | `licenses/anyio-4.13.0-LICENSE` |
| certifi | 2026.4.22 | Mozilla Public License 2.0 (MPL 2.0) | `licenses/certifi-2026.4.22-LICENSE` |
| cffi | 2.0.0 | MIT | `licenses/cffi-2.0.0-LICENSE` |
| charset-normalizer | 3.4.7 | MIT | `licenses/charset-normalizer-3.4.7-LICENSE` |
| click | 8.4.1 | BSD-3-Clause | `licenses/click-8.4.1-LICENSE.txt` |
| colorama | 0.4.6 | BSD License | `licenses/colorama-0.4.6-LICENSE.txt` |
| ctranslate2 | 4.8.0 | MIT | `licenses/ctranslate2-LICENSE.txt`(wheel 未附,取自上游) |
| faster-whisper | 1.2.1 | MIT License | `licenses/faster-whisper-1.2.1-LICENSE` |
| filelock | 3.29.0 | MIT | `licenses/filelock-3.29.0-LICENSE` |
| flatbuffers | 25.12.19 | Apache Software License | `licenses/flatbuffers-LICENSE.txt`(wheel 未附,取自上游) |
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
| tokenizers | 0.23.1 | Apache Software License | `licenses/tokenizers-LICENSE.txt`(wheel 未附,取自上游) |
| tqdm | 4.67.3 | MPL-2.0 AND MIT | `licenses/tqdm-4.67.3-LICENCE` |
| typer | 0.25.1 | MIT | `licenses/typer-0.25.1-LICENSE` |
| typing_extensions | 4.15.0 | PSF-2.0 | `licenses/typing_extensions-4.15.0-LICENSE` |
| urllib3 | 2.7.0 | MIT | `licenses/urllib3-2.7.0-LICENSE.txt` |

<!-- END AUTOGEN:PYTHON-PACKAGES -->

## 原生函式庫(隨上列 wheel 進入安裝檔)

| 元件 | 位置 | 授權 | 說明 |
|---|---|---|---|
| PortAudio | `_internal/_sounddevice_data/` | MIT 式授權 | 錄音底層,隨 sounddevice wheel 提供。原文:`licenses/portaudio-LICENSE.txt`;<http://www.portaudio.com/license.html> |
| OpenSSL 3(libcrypto / libssl) | `_internal/` | Apache-2.0 | HTTPS 用。原文:`licenses/openssl-LICENSE.txt`;<https://www.openssl.org/source/license.html> |
| Microsoft VC++ Runtime(msvcp 等) | `_internal/` | Microsoft 允許隨應用程式再散布之執行階段元件 | — |

### ⚠️ FFmpeg / x264 / x265:v0.1.4 起**不再散布**

v0.1.3(含)以前的安裝檔與 portable zip **含有 `_internal/av.libs/`**,裡面除了 FFmpeg,還有 **`libx264` 與 `libx265`——兩者都是 GPL-2.0-or-later**。而 v0.1.3 的本檔曾寫「PyAV 官方 wheel 之 LGPL 組態 build(不含 x264/x265 等 GPL 元件)」,**那句話是錯的**:從 avcodec DLL 抽出的 FFmpeg 內嵌組態字串明確是

```
--enable-version3 --enable-libx264 --enable-libx265
```

v0.1.4 起 **PyInstaller 完全不打包 av**(見 `build/rthook_no_av.py` 與 `build/local-dictate.spec` 的 `excludes`),產物內不再有任何 FFmpeg / x264 / x265 / dav1d / SVT-AV1 二進位,CI 也加了硬斷言擋住它們回來。

為什麼可以直接不要:即時聽寫**從來沒用到 FFmpeg**——麥克風音訊在 `dictate.py` 是 numpy float32 array 直接餵給模型,不走 faster-whisper 的檔案解碼路徑。代價只有「打包版不能從音檔轉錄」,要用請從原始碼執行。

## 模型與資料

| 元件 | 授權 | 原文 | 說明 |
|---|---|---|---|
| Whisper(架構與權重,OpenAI) | MIT | `licenses/whisper-LICENSE.txt` | <https://github.com/openai/whisper> |
| Systran/faster-whisper-base(安裝檔內建之 CTranslate2 轉換版權重) | MIT | 同上(Whisper 衍生) | <https://huggingface.co/Systran/faster-whisper-base> |
| Silero VAD(faster-whisper 內附 onnx 資產) | MIT | `licenses/silero-vad-LICENSE.txt` | <https://github.com/snakers4/silero-vad> |
| OpenCC 簡繁轉換辭典資料 | Apache-2.0 | `licenses/opencc-python-reimplemented-*-NOTICE.txt`,另產物內附 `_internal/opencc/NOTICE.txt` | <https://github.com/BYVoid/OpenCC> |

## 執行環境

| 元件 | 授權 | 原文 | 說明 |
|---|---|---|---|
| CPython 3.11(runtime、標準函式庫、tkinter) | PSF-2.0 | `licenses/cpython-LICENSE.txt` | <https://docs.python.org/3/license.html> |
| Tcl/Tk(tkinter 底層) | BSD 式授權 | 產物內附 `_internal/_tk_data/license.terms` | <https://www.tcl.tk/software/tcltk/license.html> |
| PyInstaller bootloader | GPL-2.0 **含例外條款**(允許任何授權之程式打包散布,不影響本專案 MIT) | `licenses/pyinstaller-COPYING.txt` | <https://pyinstaller.org/en/stable/license.html> |

---

若發現任何元件之聲明缺漏或錯誤,請開 issue,我會補正。
