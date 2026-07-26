# 交接筆記 — 2026-07-26

> 這份是給「下一個接手的人（含未來的 Claude session）」看的，不是給使用者看的。
> 使用者看 [README.md](README.md)，要做什麼看 [ROADMAP.md](ROADMAP.md)，踩過的坑看 [references/pitfalls.md](references/pitfalls.md)。

## 一句話

從「想用講的取代打字」到「開源專案 + 可安裝的 exe + 第一個外部使用者」，一天內完成。
**目前狀態：v0.1.2 已發佈，可以給人用。**

---

## ⚠️ 最重要的一件事：兩份拷貝

| 位置 | 是什麼 |
|---|---|
| `C:\Users\jason\.claude\skills\語音轉錄\dictate\` | **Jason 日常實際在跑的**（開發版，連同他的 `config.json` / `vocab.txt`，含客戶名，不進版控） |
| `C:\Claude 作品\local-dictate\` | 開源 repo（就是這裡） |

**改程式碼要兩邊一起更新。** 目前是手動 `Copy-Item`。
標準流程：改 skill 目錄 → `python -m py_compile` → 跑 `tests/test_pure.py` → 複製到 repo → 重啟引擎 → commit。

重啟指令（Jason 的開發版）：
```powershell
Get-CimInstance Win32_Process -Filter "Name='pythonw.exe'" |
  Where-Object { $_.CommandLine -like '*dictate*' } | Stop-Process -Force
Start-Process "C:\Users\jason\AppData\Local\Programs\Python\Python311\pythonw.exe" `
  -ArgumentList '"C:\Users\jason\.claude\skills\語音轉錄\dictate\dictate.py"'
```

---

## 現在到哪了

**已發佈**：v0.1.0 → v0.1.1 → v0.1.2（https://github.com/jason201385-commits/local-dictate/releases）

- `local-dictate-setup-0.1.2.exe`（186MB，內建 base 模型，per-user 安裝不跳 UAC）
- `local-dictate-portable.zip`（94MB）
- CI 自動出 release：打 `v*` tag 就跑

**外部使用者**：1 位（Riley），已回報 2 個問題並修正。Repo 有 1 個 fork、1 個 issue（徵求硬體實測數字）。

---

## 唯一還沒做、但很重要的驗證

**乾淨 Windows VM 的完整流程**：安裝 → 首次啟動 → 錄音 → 轉寫 → 貼上 → 升級覆蓋 → 解除安裝。

已做的是**開發機上**的完整安裝驗證（下載 → SHA256 相符 → 靜默安裝 → 執行 → 靜默解除安裝，全部通過）。
但開發機有一堆「剛好裝過」的東西，PyInstaller 可能靠了某個沒被打包進去的 DLL。
**這一格不能自己打勾。**

---

## 今天所有 bug 的共同形狀

**「有時候好、有時候壞」幾乎從來不是一個 bug。**

一整天抓到的都是同一類：熱鍵漏字進輸入框、麥克風拿到靜音串流、Windows 前景鎖靜默失敗、目標視窗鎖太早、面板沉到底層、首次啟動默默下載。
每一個單獨看都很小，疊在一起就變成「這東西不能用」，而且修掉一個症狀還在，會讓人誤以為修錯方向。

**除錯的關鍵句**：先別問「為什麼不行」，先問「**什麼時候可以、什麼時候不行**」。

三個最貴的教訓，細節都在 `references/pitfalls.md`：

1. **`rc=0` 是行程的工作證明，不是模型/使用者的工作證明**。CI 綠燈 ≠ 裝得起來——實際下載安裝一次才抓到「首次啟動會默默下載 463MB」。
2. **prompt 擋不住的，要用程式擋**。整理層會把使用者的口述當指令執行（18 秒口述 → 1998 字規格書）。防線是「輸出超過原文 1.5 倍就丟棄」那段程式，**不要為了輸出更漂亮把它拿掉**。
3. **樣式位元 ≠ 實際狀態**。`WS_EX_TOPMOST` 有設不代表視窗真的在最上層那一層。

---

## 已知還沒解的問題

- **視窗有焦點 ≠ 輸入框有游標**。Windows 對 Qt/Chromium 這類自繪介面不誠實回報文字游標，所以程式**無法**判斷貼上會不會生效。目前的解法是「文字一律同時放剪貼簿 + 面板給 `📋` 按鈕」。要真正解決可能得走 UI Automation，還沒評估。
- **macOS 完全沒有**。轉寫核心本來就跨平台，缺的是 OS 整合層，對照表在 `docs/macos.md`，缺 Mac 實機數字。
- **`setup_ai.py` 的「貼上金鑰」分支沒實測過**（需要真的輸入）。選單與現況顯示已驗證。

---

## 下一步（依 ROADMAP 排序）

1. **乾淨 VM 驗證** ← 最該做的，因為現在是拿使用者當白老鼠
2. 首次啟動精靈（把 `doctor.py` / `tune.py` 藏進去，使用者不該知道它們存在）
3. 模型管理器（base 即用 → small 背景升級 → medium 明確選配）
4. 內嵌 `llama-server.exe` sidecar，讓「整理」也能零設定離線

**不要做**的清單在 ROADMAP 底部，每一條都有理由，別重新發明。

---

## 給接手的人的提醒

- 動 `dictate.py` 之前先讀 `references/pitfalls.md`，那 11 條每一條都花過很久
- 改熱鍵預設值時 CI 會擋（`tests/test_pure.py` 有「不可以是 Alt+Space/Enter」的回歸測試）
- `config.json` / `vocab.txt` / `dictate.log` 在 `.gitignore` 裡，**不要手動 git add**
- Jason 的環境有 PostToolUse hook 會自動 commit，檔案一寫出來就進版控，**來不及先審**。公開 repo 的第一個 commit 前先 `git ls-files` 確認清單
