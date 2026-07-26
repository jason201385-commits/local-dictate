# macOS 移植對照表

> **現況：口述引擎本體只有 Windows 版。** 這份文件把「還缺什麼」講清楚，讓有 Mac 的人可以直接動手，不用先花一天做考古。
>
> ⚠️ 本文件的 macOS 對應方案**沒有在 Mac 實機驗證過**（作者只有 Windows）。請把它當地圖，不是保證。實作後請回報真實結果，我會照實修正這份文件。

## 先講結論：哪些已經是跨平台的

`dictate.py` 大致可以切成兩層。**下層本來就跨平台，卡住的是上層。**

| 層 | 做什麼 | 跨平台？ |
|---|---|---|
| 音訊擷取 | `sounddevice` 常開串流 | ✅ 已跨平台 |
| 語音辨識 | `faster-whisper` | ✅ 已跨平台（但加速方式不同，見下） |
| 簡繁轉換 | `opencc` | ✅ |
| 專有名詞字典 / 正規化 | 純 Python | ✅ |
| 整理層 | HTTP 呼叫 | ✅ |
| 剪貼簿 | `pyperclip`（Mac 走 pbcopy/pbpaste） | ✅ |
| **全域熱鍵** | `RegisterHotKey` + 訊息迴圈 | ❌ Win32 |
| **判斷目標視窗** | `GetForegroundWindow` 等 | ❌ Win32 |
| **還原焦點** | `SetForegroundWindow` + `AttachThreadInput` | ❌ Win32 |
| **不搶焦點的小面板** | `WS_EX_NOACTIVATE` | ❌ Win32 |
| **提示音** | `winsound.Beep` | ❌ Win32 |
| **開機自啟 / 啟動快速鍵** | `.lnk` 的快速鍵屬性 | ❌ Win32 |

`doctor.py` 與 `tune.py` 已經改成跨平台，Mac 上可以直接跑，會誠實告訴你缺什麼。

## 加速：Mac 這塊要重新想

CTranslate2（faster-whisper 的推論引擎）**目前沒有 Apple GPU（Metal/MPS）後端**，所以 Mac 上是**純 CPU** 跑。Apple Silicon 的 CPU 不慢，`small` 應該可用，但要吃到 GPU 得換引擎：

- **mlx-whisper**（Apple MLX，走 Apple Silicon GPU）
- **whisper.cpp** 的 Metal 後端

若要換引擎，`Engine.transcribe()` 是唯一需要改的地方——它的輸入是 numpy 音訊、輸出是字串，介面很窄。**建議做成可插拔的後端，而不是分岔兩份程式。**

## 逐項對照

| Windows 現況 | macOS 可能的對應 | 難度 |
|---|---|---|
| `RegisterHotKey` + 訊息迴圈 | `pynput.keyboard.GlobalHotKeys`（Mac 版走 CGEventTap，**需要「輔助使用」權限**）；或 `Quartz` 的 `CGEventTapCreate` 自己做 | 中 |
| `GetForegroundWindow` + 視窗標題 / 執行檔 | `NSWorkspace.sharedWorkspace().frontmostApplication()`（pyobjc），或 `osascript -e 'tell app "System Events" to name of first process whose frontmost is true'` | 低 |
| `SetForegroundWindow` + `AttachThreadInput` | `osascript -e 'tell application "X" to activate'`，或 pyobjc 的 `activateWithOptions_` | 低 |
| `WS_EX_NOACTIVATE` 小面板 | tkinter 做不到。要用 pyobjc 開 `NSPanel` 並設 `NSNonactivatingPanelMask`；**或**接受面板會搶焦點，改成「錄音開始時記住目標 app、貼上前重新 activate」（這條路現在的程式已經有了） | 高（面板）／低（改走 activate） |
| `winsound.Beep` | `afplay` 播短音檔，或 `NSSound`；也可以直接用 `sounddevice` 播一段正弦波（這樣兩邊共用一份程式） | 低 |
| 模擬 Ctrl+V | 改成 **Cmd+V**（`keyboard.Key.cmd`） | 低 |
| `.lnk` 快速鍵 + 開機自啟 | 開機自啟用 LaunchAgent plist；啟動快速鍵用「捷徑」App 或 Automator 服務 | 低 |
| 麥克風權限檢查（讀登錄檔） | 讀 TCC 資料庫不可靠，改成**實際試錄 0.5 秒看音量**（`doctor.py` 已經有這段） | 低 |
| `GetGUIThreadInfo` 焦點診斷 | 沒有對應，Mac 版直接省略即可（本來就只是診斷用） | — |

## 建議的動手順序

1. **先讓 `doctor.py` / `tune.py` 在你的 Mac 上跑一遍**，把真實數字貼進 issue（晶片、核心數、各模型耗時）。這一步不用寫任何程式，但最有價值——現在整份文件缺的就是 Mac 真實數字。
2. **把平台相依的呼叫抽成一個介面**（`beep / current_app / focus_app / send_paste / register_hotkeys / make_panel`），Windows 版是現有實作，Mac 版另寫一份。**不要複製整個檔案分岔。**
3. 先做**沒有小面板的版本**（純熱鍵）。面板的「不搶焦點」是最難的一塊，先跳過也完全可用。
4. 最後再處理 `NSPanel`。

## 已知會咬人的地方

- **macOS 權限**：全域熱鍵要「輔助使用」、麥克風要「麥克風」權限，兩個都要使用者手動去系統設定開，而且**改過程式碼後權限可能要重新授權**。
- **Cmd+V 而不是 Ctrl+V**：這個漏掉的話症狀跟 Windows 上那個「貼上沒反應」一模一樣，會查很久。
- **Windows 那些坑不一定適用**：`Alt+Space` 系統選單、`Ctrl+Alt` 被當成 AltGr 打出字元——這兩個是 Windows 專屬。Mac 有自己的一套（例如 Cmd 系快速鍵被系統先吃掉），請重新踩、重新記錄，不要照抄。
