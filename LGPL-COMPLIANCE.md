# LGPL 元件與你的替換權利

安裝檔內有**一個** LGPL 授權的元件。LGPL 給你的權利是:**你可以用自己修改過的版本替換它**,而且本專案提供做到這件事所需的一切。

| 元件 | 授權 | 在安裝檔的位置 |
|---|---|---|
| pynput 1.8.2(全域熱鍵/模擬按鍵) | LGPL-3.0(`licenses/pynput-1.8.2-COPYING.LGPL`) | 打包進 PyInstaller 的 Python 模組 |

> **v0.1.3 以前這裡還列了 FFmpeg,那份說明有兩個錯**:一是把它標成 LGPL-2.1+(實際組態是 `--enable-version3`,即 v3),二是宣稱不含 x264/x265(實際含有,而那兩個是 GPL-2.0+)。
> **v0.1.4 起已完全不打包 FFmpeg**,所以這一項不再存在——詳見 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。要從音檔轉錄請從原始碼執行(`pip install av`),那時 FFmpeg 是你自己裝的,授權關係在你與上游之間。

## 替換 pynput(重新打包,約 10 分鐘)

pynput 是純 Python 套件,打包在 PyInstaller 產物內。要用修改版:

```bash
git clone https://github.com/jason201385-commits/local-dictate
cd local-dictate
pip install -r requirements.txt        # 或先 pip install 你修改過的 pynput
pip install 你的-pynput-修改版 --force-reinstall
pip install pyinstaller
python -m PyInstaller build/local-dictate.spec --noconfirm
```

產物在 `dist/local-dictate/`,功能與官方安裝檔相同(內建模型另從 <https://huggingface.co/Systran/faster-whisper-base> 下載,或直接沿用 `%LOCALAPPDATA%\local-dictate\models` 既有檔案)。

- pynput 原始碼:<https://github.com/moses-palmer/pynput>
- 本專案完整原始碼(含打包 spec 與 CI 流程):本 repo

## 授權原文

`licenses/` 目錄收錄 LGPL-2.1、LGPL-3.0 與 GPL-3.0(LGPL-3.0 為 GPL-3.0 之補充條款,依 LGPL-3.0 要求一併提供)全文,隨安裝檔安裝。
