# 安裝與調校

## 硬條件（缺一不可）

| 條件 | 沒有會怎樣 |
|---|---|
| **Windows** | 完全不能跑（整套 Win32 API）。macOS 見 `docs/macos.md` |
| **Python 3.10+** | 語法過不了 |
| **麥克風 ＋ Windows 麥克風權限** | 收不到聲音，而且不會有明顯錯誤 |
| **約 3GB 磁碟 ＋ 首次下載要網路** | 模型下載失敗 |

選配：**NVIDIA 顯卡**（沒有就退 CPU，慢 5 倍以上）。

## 三步驟

```bash
pip install -r requirements.txt      # 或雙擊 安裝.bat
python doctor.py                     # 環境健檢，缺什麼直接告訴你
python tune.py --apply               # 依這台硬體挑模型，寫進 config.json
```

然後雙擊 `啟動口述.bat`，右下角出現小面板就能用。第一次啟動會下載模型（約 1.5GB）。

`建立快捷鍵.bat` 會多做兩件事：`Ctrl+Alt+V` 隨時叫回引擎、開機自動啟動。

## `doctor.py` 檢查什麼

作業系統、Python 版本、七個套件、tkinter、GPU 與 CUDA、**Windows 麥克風權限**、輸入裝置並實際試錄一次、模型快取、磁碟空間、API key、資料夾寫入權限。

每個問題都直接給修法，最後統整「哪些會讓它不能用、哪些只是建議」。

## `tune.py` 怎麼決定設定

```bash
python tune.py            # 剖析硬體 → 規則式建議（秒出，不下載模型）
python tune.py --bench    # 實跑基準測試，用真數字決定
python tune.py --apply    # 寫進 config.json
```

`--bench` 用系統內建語音合成做一段中文樣本，實跑建議值附近的幾個模型，**挑出「這台能在 2.5 秒內轉完」的最大模型**。不用看規格表猜。

### 為什麼不能給一組通用預設

「有沒有顯卡」不是二分法。VRAM 決定塞得下多大的模型、CPU 核心數決定沒顯卡時有多痛。同一份預設值在不同機器上，有人 1 秒、有人 15 秒。

### 參考數字（作者實測，你的機器會不同）

同一段 **11 秒中文音檔**：

| 環境 | 設定 | 耗時 |
|---|---|---|
| RTX 4050 Laptop 6GB | `medium` + beam 5 | 1.2 秒 |
| 同上 | `large-v3` + beam 1 | 1.6 秒 |
| CPU（22 邏輯核心）| `medium` | 6.7 秒 |
| 同上 | `small` | 3.3 秒 |
| 同上 | `base` | 1.2 秒（但辨識明顯變差）|

⚠️ **不要用 `medium` + beam 1**：只快 0.25 秒，但會把英文品牌名聽錯。
⚠️ CPU 那組是在 22 核心的機器上測的，**核心少的筆電會再慢一截**。

## `config.json` 主要欄位

| 欄位 | 說明 |
|---|---|
| `model` | `tiny`/`base`/`small`/`medium`/`large-v3` |
| `beam_size` | 預設 5 |
| `to_traditional` | OpenCC 簡轉繁，預設 `true` |
| `diary_dir` | 口述日記存放處。留空＝`家目錄\Documents\口述日記` |
| `hotkeys` | 全域熱鍵。⚠️ **不要用 Alt+Space / Alt+Enter**，理由見 `pitfalls.md` |
| `output_method` | `paste`（預設）／`type`。`type` 在中文輸入法「中」模式會吃掉英數與全形標點，只作備援 |
| `polish.enabled` | 整理層總開關。設 `false` ＝ **100% 離線** |

## `vocab.txt` 是準確度最大的槓桿

一檔兩用：

1. 餵給 whisper 的 `hotwords` — 講到這些字時辨識率明顯拉高
2. 當「正規寫法表」— whisper 會自作主張把 `myBrand` 寫成 `MyBrand`，程式會不分大小寫比對換回你寫的版本

有 300 字上限，**最常講的放最上面**。加專有名詞的效果通常比換更大的模型明顯。

⚠️ `vocab.txt` 已被 `.gitignore` 排除（裡面常有客戶名與專案代號），不要手動 `git add`。

## 整理層（選配）

預設走 [NVIDIA NIM](https://build.nvidia.com/)（有免費額度），讀環境變數 `NVIDIA_API_KEY`。**沒設 key 就自動退回貼原文，不會壞掉。**

想換別家 OpenAI 相容 API：改 `config.json` 的 `polish.url` 與 `polish.model`。
