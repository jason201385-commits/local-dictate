---
name: local-dictate
description: 本機繁體中文語音輸入（faster-whisper，音訊不出網、無字數上限、免費）。用於安裝與調校，以及排查「按了沒反應」「字跑到別的視窗」「有時候好有時候壞」「輸出簡體字」「辨識不準」「太慢」等狀況。也可用於了解 Windows 桌面自動化的已知陷阱（全域熱鍵漏字、前景鎖、音訊串流靜音、LLM 加工層把內容當指令執行）。觸發詞：「口述」「用講的」「聽寫」「語音輸入」「不想打字」「local-dictate」。
---

# local-dictate

點一下講話 → faster-whisper 在**本機**轉寫 → 字貼回游標所在處。音訊不離開電腦。

專案本體 `dictate.py`（Windows + Python）。macOS 尚未支援，移植對照見 `docs/macos.md`。

## 先做這件事：讓程式自己講話，不要用猜的

| 使用者的狀況 | 第一個動作 |
|---|---|
| 還沒裝 / 裝不起來 | `python doctor.py` — 逐項檢查並直接給修法 |
| 不確定自己電腦跑不跑得動 | `python tune.py`（加 `--bench` 實測、`--apply` 套用） |
| 裝好了但行為怪 | 讀專案資料夾裡的 `dictate.log` |
| 想改程式碼 | **先讀 `references/pitfalls.md`**，那些坑每個都花了很久才抓到 |

## 路由

| 需要 | 讀 |
|---|---|
| 安裝、硬體需求、選模型、調參數 | `references/setup.md` |
| 排查（log 訊息 → 根因 → 修法） | `references/troubleshoot.md` |
| 改程式碼前的已知陷阱 | `references/pitfalls.md` |
| macOS 移植 | `docs/macos.md` |

**不要在對話裡重新推導這些結論**——都是實測記錄下來的，直接讀檔。

## 操作速查

- 啟動／叫回：`Ctrl+Alt+V`（跑過 `建立快捷鍵.bat` 之後）；或雙擊 `啟動口述.bat`
- 上字：`Ctrl+Alt+Z`｜上字並送出：`Ctrl+Alt+X`｜日記：`Ctrl+Alt+D`｜結束：`Ctrl+Alt+Q`
- 面板：左鍵點一下開始、再點結束；**右鍵取消**；`✕` 要點兩次才關
- 錄音時面板最大那行 = 字會去哪；下面那條 = 有沒有收到聲音

## 三條紅線

1. **`config.json` / `vocab.txt` / `dictate.log` 不進版控**——含個人路徑、客戶名、口述內容片段。已在 `.gitignore`，不要手動 `git add`。
2. **講機密時把面板的 `✨整理` 關掉**（變灰）＝純本機。聲音本來就不出網，整理層是唯一會把**文字**送出去的地方。
3. **`polish()` 裡的長度上限不要拿掉**。那是擋「整理模型把你的口述當成指令去執行」的唯一防線，理由見 `references/pitfalls.md`。
