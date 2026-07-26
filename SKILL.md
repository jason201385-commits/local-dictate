---
name: local-dictate
description: 本機繁體中文語音輸入（faster-whisper，音訊不出網）。協助安裝、設定、排查「按了沒反應／字跑到別的視窗／輸出簡體字／辨識不準」等問題。觸發詞：「口述」「用講的」「聽寫」「語音輸入」「不想打字」「local-dictate」。
---

# local-dictate — 本機語音輸入

按一下講話 → faster-whisper 在本機轉寫 → 字貼回游標所在處。音訊不離開電腦、無字數上限、免訂閱。
專案本體：`local-dictate/dictate.py`（Windows + Python）。

## 先確認它在跑

小面板應該在螢幕右下角。不在的話：

```powershell
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" | Where-Object { $_.CommandLine -like '*dictate*' }
```

沒有就按 **`Ctrl+Alt+V`**（跑過 `建立快捷鍵.bat` 之後隨時可叫回），或雙擊 `啟動口述.bat`（無主控台視窗）。要看錯誤訊息改用 `除錯-顯示主控台.bat`。

程式有具名 mutex 單一實例鎖：已經在跑時再啟動只會跳提示，不會產生第二個實例（兩個實例會搶同一組全域熱鍵、講一次錄兩份）。
面板的 `✕` 要點兩次才會關（第一次只是詢問），避免手滑關掉。

## 排查順序（一律先看 log，不要用猜的）

`dictate.log` 就在專案資料夾裡，每次都會記下目標視窗、貼到哪、辨識到的前 40 字。

| log 出現 | 意思 | 怎麼修 |
|---|---|---|
| `✗ 幾乎沒收到聲音（RMS …）` | 麥克風靜音／被別的程式佔用／選錯裝置 | 檢查 Windows 音效設定的預設輸入裝置 |
| `✗ 太短（不到 0.3 秒）` | 連點兩下了 | 這是 toggle：點一下開始、講、再點一下結束 |
| `✗ 有收到聲音但辨識不出` | 太小聲或雜訊太多 | 靠近麥克風、講大聲一點 |
| `⚠ 整理結果異常膨脹` | 整理模型把口述當指令執行了 | 已自動改貼原文；內容偏指令性時把 `✨整理` 關掉 |
| `⚠ 焦點已不在原目標視窗` | 中途切換視窗了 | 已只貼上、沒自動送出（這是安全鎖，不是 bug） |
| **完全沒有新行** | 熱鍵被別的軟體搶走／程式沒在跑 | 先確認程序在跑；再改 `config.json` 的 `hotkeys` |

## 常見要求怎麼處理

- **「辨識不準」** → 第一個動作永遠是叫他把常講的專有名詞加進 `vocab.txt`（一行一個，常講的放上面，有 300 字上限）。這是準確度最大的槓桿，效果比換模型明顯。再不夠才把 `config.json` 的 `model` 換成 `large-v3` 且 `beam_size` 設 1。
- **「輸出簡體字」** → 裝 `opencc-python-reimplemented`，確認 `to_traditional` 是 `true`。
- **「字跑到別的視窗」** → 它貼回「開始講話時的前景視窗」。若兩個 app 視窗標題相同（例如 Claude Code 與 Claude 桌面版都叫「Claude」、執行檔都叫 `claude.exe`），在 `dictate.py` 的 `APP_NAMES` 加一行「路徑片段 → 顯示名稱」即可分辨。錄音時面板會顯示目標，不對可**右鍵取消**。
- **「太慢」** → 確認有跑在 GPU（log 會寫 `模型就緒 GPU/...`）。退到 CPU 通常是缺 `nvidia-cublas-cu12` / `nvidia-cudnn-cu12`。
- **「我不想讓任何東西出網」** → `config.json` 的 `polish.enabled` 設 `false`，或把面板上的 `✨整理` 點成灰色。聲音本來就不出網，整理層是唯一會送文字的地方。

## 改程式碼之前一定要知道的事

這些都是踩過才修的，動到相關區域前先讀 README 的「踩過的坑」：

1. 專有名詞走 `hotwords`，**不要**塞 `initial_prompt`（後者從尾端截斷，會把繁中指令切掉→吐簡體）
2. 暖機必須 `vad_filter=False`，否則靜音被濾光、根本沒暖到
3. `.bat` 檔內容必須純 ASCII（cmd 用 cp950 讀 .bat，中文會把指令切爛）
4. 面板要 `WS_EX_NOACTIVATE`，且要 `GetAncestor()` 取頂層 HWND ＋ `SetWindowPos(FRAMECHANGED)` 才生效
5. **整理層有 prompt injection 風險**：口述內容含指令時模型會照做（實測 18 秒口述 → 1998 字規格書）。防線是「長度硬上限」那段程式，**不要為了讓輸出更漂亮就把它拿掉**
6. `pythonw` 下 `sys.stdout is None`，任何 `print()` 都會炸

## 紅線

- `config.json` / `vocab.txt` / `dictate.log` 都在 `.gitignore` 裡——它們含個人路徑、客戶名、口述內容片段。**不要手動 git add**。
- 講客戶機密、金鑰、報價細節時，把 `✨整理` 關掉（灰色）＝純本機，文字不出網。
