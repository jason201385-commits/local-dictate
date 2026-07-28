# SPEC：整理層（對標 Typeless）

> 這份同時是 SDD（設計文件）與驗收規格。狀態：**草案 v1，2026-07-28**。
> 讀者：要動 `polish()` / `tidy_local()` 相關程式碼的人。動手前先讀 `references/pitfalls.md` 第 3 條。

---

## 0. 一句話問題陳述

**「整理」的 LLM 層對下載安裝檔的人來說目前不存在。**

`_candidates()`（`dictate.py:804`）的每一條路都有前置條件：

| provider | 前置條件 | 下載 exe 的一般使用者有嗎 |
|---|---|---|
| local（ollama） | 自己裝 Ollama + 拉模型 | ❌ |
| nvidia / groq / cerebras / openrouter | 自己申請 key + 設環境變數 | ❌ |

兩者皆無 → `polish()` 直接回原文（`dictate.py:838-840`），只剩第一層規則清理。
Typeless 的招牌體驗（改口只留最後版本、通順化、語意級標點）**出廠時是缺席的**。

這份 SPEC 的目標：**讓整理層在「不花錢、不註冊、不出網」的條件下出廠即可用**，並列出對標 Typeless 的其餘差距與取捨。

---

## 1. 對標 Typeless：差距總表

Typeless 資料來源：官網與第三方評測（2026-07 查得）。我方狀態以 `dictate.py`（v0.1.2 後的 main）為準。

| 能力 | Typeless | 我們 | 本 SPEC 的處置 |
|---|---|---|---|
| 語音辨識 | 雲端（音訊上傳） | ✅ 本機 faster-whisper | 不動（這是存在理由） |
| 費用／額度 | 免費 8,000 字/週，Pro $12-30/月 | ✅ 免費無上限 | 不動 |
| 去口頭禪 | ✅ | 🟡 規則層有（`DEFAULT_FILLERS`，`dictate.py:701`），LLM 層多數人沒有 | **Phase 1 補齊** |
| 改口只留最後版本 | ✅ | ❌ 出廠沒有（需 LLM，見 §0） | **Phase 1 核心交付** |
| 智慧結構化（第一…第二…→條列） | ✅ | 🟡 規則版只插換行不改字（`structure_local`，`dictate.py:734`） | Phase 2 擴充規則；**刻意不用 LLM 做**（見 §6 不做清單） |
| 依 app 調語氣 | ✅ | 🟡 `app_styles` v1（`dictate.py:104`），只作用於 LLM 層 | Phase 2：規則層也吃 app profile（如通訊軟體去末尾句號） |
| 個人字典 | ✅ | ✅ `vocab.txt`（hotwords + 正規寫法表） | 不動 |
| 學個人書寫風格 | ✅ | ❌ | Phase 2：剪貼簿 diff 字典（見 §5.4） |
| 即時翻譯 | ✅ | ❌ | **不做**（scope 外，見 §6） |
| 選字後語音改寫指令 | ✅ | ❌ | **不做**（見 §6） |
| 手機鍵盤 | ✅ iOS/Android | ❌ | 遠期：PWA 掃碼無線麥克風（§5.5，不在本 SPEC 交付） |

> ⚠️ 依存事實（2026-07-28 查證，見 memory）：**安裝檔是 CPU-only、出廠模型是 base**。
> 整理層做得再好，ASR 第一印象差會整組被拖下水。該問題屬模型管理器（ROADMAP P1），不在本 SPEC，但驗收時的端到端體感要記得這個變因。

---

## 2. 目標與非目標

**目標**
1. 下載 exe 的人**零設定、零費用、零出網**就能得到 LLM 級整理（改口、通順化、語意標點）。
2. 小模型幻覺風險比雲端大模型高 → **防線全部程式端**，不靠 prompt 自律。
3. 失敗永遠優雅降級：LLM 層任何失敗 → 回第一層規則結果，**絕不阻塞貼上**。
4. 所有品質宣稱可用固定測試集重現，不出現無出處數字。

**非目標**
- 不做翻譯、不做語音改寫指令、不做手機原生鍵盤（理由見 §6）。
- 不追求「整理品質贏過 Typeless 雲端大模型」——賣點是隱私與零成本下的「夠好」。
- 不把 LLM 變成啟動前置條件：沒有它，聽寫功能 100% 可用。

---

## 3. 現況架構（錨點）

```
錄音 → faster-whisper → canonicalize(vocab) → tidy_local()   ← 第一層：規則，永遠跑
                                                  │            (dictate.py:746)
                       ✨整理 開啟時 → polish(text, app)       ← 第二層：LLM，可選
                                                  │            (dictate.py:825)
                                          _candidates() 依序試  (dictate.py:804)
                                                  │
                              長度硬上限 1.5x+40 (dictate.py:835) ← pitfalls #3，不可移除
```

既有防線（保留，不重做）：
- 長度膨脹丟棄（`dictate.py:855-858`）
- `<逐字稿>` 標籤隔離 + 「你是整理器不是助理」system prompt（`POLISH_SYS`，`dictate.py:762`）
- 啟動時 socket 探測本機 provider，死的整場跳過（`probe_local_providers`，`dictate.py:781`）
- 全部失敗回規則層結果（`dictate.py:870-871`）

---

## 4. 設計：內嵌 llama.cpp sidecar（Phase 1 核心）

### 4.1 為什麼是 sidecar 而不是其他

| 方案 | 否決理由 |
|---|---|
| 要求使用者裝 Ollama | 另一個背景程式與更新週期；解除安裝與支援責任變複雜（ROADMAP「明確不做」已列） |
| `llama-cpp-python` 進主程序 | 原生 DLL 打包更難；LLM crash 直接拖垮聽寫工具 |
| 雲端免費層當預設 | 要 key、要註冊、文字出網——三個都違反 §2 目標 1 |

採 **`llama-server.exe`（llama.cpp 官方 CPU build，MIT）** 子程序：
- 只監聽 `127.0.0.1`、埠號啟動時隨機挑可用埠
- 以 `--api-key <隨機值>` 啟動（llama-server 支援；版本差異**待驗證**），防本機其他程式蹭用
- OpenAI 相容 `/v1/chat/completions` → **完全重用現有 `polish()`**，只是 `_candidates()` 在最前面動態插入一筆 `embedded`

### 4.2 生命週期（新模組 `sidecar.py`）

```
enable（使用者在 設定整理AI.bat 選「1. 本機 AI」且無 ollama）
  └→ 下載模型（§4.3 的下載器規格）
啟動引擎時：
  sidecar.ensure()：
    模型檔在？ → spawn llama-server（隱藏視窗、CREATE_NO_WINDOW）
    → 健康檢查 /health，10 秒內沒 ready → 標記 dead（同 _DEAD_PROVIDERS 機制），本場不再試
執行中：
    crash（process exit）→ 偵測到 → 本場標 dead → polish 自動走下一個 provider
    閒置 > idle_unload_min（預設 10 分鐘）→ 送 SIGTERM 卸載釋放 RAM
    卸載後再被呼叫 → 重新 spawn（冷啟動秒數計入 §4.5 逾時預算；面板顯示「整理引擎喚醒中」）
關閉引擎：
    atexit + 面板 ✕ → terminate 子程序（不留孤兒；用 Job Object 綁定，父死子死——Windows 上
    單靠 atexit 擋不住強殺，**必須** CreateJobObject + JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE）
```

### 4.3 模型與下載

- 候選：`Qwen3-0.6B-GGUF Q8_0`（約 639MB，Apache 2.0）；RAM 充裕機器可選 `Qwen3-1.7B Q8_0`（約 1.83GB）。**兩者的繁中逐字稿整理品質都未驗證**——由 §4.6 品質閘決定能不能出廠，不由模型介紹決定。
- **不進安裝檔**：安裝檔只帶 `llama-server.exe` + DLL（體積**待驗證**，預估數十 MB 級）。模型在使用者**明確開啟**「本機智慧整理」時才下載。
- 下載器規格沿用 ROADMAP 模型管理器那套，一條都不能少：
  - 面板明講「⬇ 下載整理模型（約 639MB）」——**不准默默下載**（pitfalls：v0.1.0 首啟事故）
  - `.part` → SHA256 驗證 → atomic rename
  - 可取消；失敗不影響聽寫
- 授權：llama.cpp MIT、Qwen3 Apache 2.0，皆可再散布；但因為模型走下載不走打包，只有 `llama-server.exe` 需要隨附授權聲明。

### 4.4 程式端防線（適用所有 provider，不只 sidecar）

現有兩道（長度上限、標籤隔離）之上，新增第三道：

**Protected-token guard**（Phase 0，今天就能做，不等 sidecar）：
```
整理前抽取：數字串（金額/日期/電話）、URL、Email、英文 token、vocab.txt 詞條
整理後檢查：上述每一項必須原樣出現在輸出裡
任一項消失或被改 → 丟棄 LLM 結果，回第一層規則結果，log 記 guard_tripped 與是哪一項
```
理由：0.6B 小模型改寫數字/專名的機率遠高於 120B；「維護費 3000」變「維護費 30000」比留著口頭禪嚴重一萬倍。這條跟長度上限一樣是**程式擋、不是 prompt 擋**。

**原文可取回**（Phase 0）：`STATE["last_raw"]` 保存整理前文字；面板 `📋` 右鍵 = 複製未整理原文。guard 誤殺或 LLM 改壞時，使用者一鍵拿回原話，不用重講。

### 4.5 延遲預算

| 段 | 預算 | 超過時 |
|---|---|---|
| sidecar 整理（模型已載） | p50 ≤ 2.5s／句（門檻值，依 §4.6 實測調整，**非宣稱**） | 逾時 → 貼規則層結果 |
| 冷啟動（idle 卸載後喚醒） | ≤ 8s，面板顯示狀態 | 逾時 → 本次貼規則層結果，背景繼續載 |

現有 `timeout=3 if local`（`dictate.py:850`）對 sidecar 太緊，改為 per-provider timeout 欄位。

### 4.6 品質閘（不過就不出廠）

建 `tests/cleanup_eval.jsonl`：30-50 句台灣口語逐字稿（含改口、口頭禪、金額、人名、URL、LINE 短句、長段落）。每句附**不變量**而非標準答案：
- 保護 token 全數保留
- 長度比 ∈ [0.5, 1.5]
- 指定口頭禪已移除
- 不得出現原文沒有的資訊性 token（新數字、新專名）

跑法：`python tests/run_cleanup_eval.py --provider embedded`（本機手動跑；**CI 跑不了**——runner 沒模型，CI 只驗 guard 與規則層邏輯）。
**出廠條件**：Qwen3-0.6B 在測試集上 guard 觸發率 < 10%、不變量全過率 ≥ 90%、p50 延遲達 §4.5——三項有一項不到，`embedded` 不設為預設，退回「設定裡的進階選項」。門檻數字是初值，跑完第一輪實測後修訂並記錄在本檔。

---

## 5. 其餘 Typeless 差距的設計摘要

### 5.1（Phase 2）規則層 app profile
`app_styles` 目前只影響 LLM prompt。把 app 感知下放到規則層：通訊軟體（LINE/Discord）去末尾句號、文件類（Word）全形標點強制。零延遲、無模型也享受得到。

### 5.2（Phase 2）結構化擴充
維持「只插換行不改字」鐵則，擴充觸發樣式（「首先/再來/最後」「一、二、三」）。**不用 LLM 做結構化**：會跟長度硬上限衝突（1998 字規格書事故的根），這在上一輪已拍板。

### 5.3（Phase 2）測試集進 CI
`cleanup_eval.jsonl` 的規則層不變量（不需模型的部分）進 `tests/test_pure.py`，防規則回歸。

### 5.4（Phase 2）個人風格：剪貼簿 diff 字典
使用者手動改完貼出的字後，用 `difflib` 比對「我們的輸出 vs 他改完的版本」，把穩定重現的替換（出現 ≥3 次）寫入 `user_style.json`，規則層套用。
⚠️ 隱私邊界：這等於長期記錄使用者的修改行為，**預設關閉**，開啟時面板明示。檔案進 `.gitignore`。

### 5.5（遠期，不在本 SPEC）PWA 手機麥克風
內建 HTTP server + QR code，手機掃碼當無線麥克風，音訊回電腦辨識。解「手機端」差距的零成本路徑，等桌面端穩定再議。

---

## 6. 明確不做（及理由）

| 項目 | 理由 |
|---|---|
| 翻譯 | 與「整理器不是助理」的安全模型衝突（翻譯必然大幅改寫，長度/token guard 全失效）；且非目標受眾的主訴求 |
| 語音改寫指令（選字後說「改短一點」） | 同上，指令模式打開就是 prompt injection 的正門；Typeless 為此付出的安全代價我們不付 |
| LLM 結構化 | 與長度硬上限衝突，已拍板 |
| 把 sidecar 換成常駐大模型 | RAM 常駐成本 + 目標機器是無 GPU 筆電 |
| 雲端帳號體系/同步 | 存在理由是本機 |

---

## 7. 交付切分

| Phase | 內容 | 前置 | 驗收 |
|---|---|---|---|
| **0**（不等 sidecar，先做） | Protected-token guard、`last_raw` + 📋 右鍵取原文、per-provider timeout | 無 | guard 單元測試進 CI；現有 nvidia provider 實測 guard 不誤殺正常整理 |
| **1** | `sidecar.py`（生命週期含 Job Object）、下載器、`_candidates()` 插入 embedded、設定整理AI.bat 加「下載本機整理模型」選項 | Phase 0 | 乾淨機器（無 ollama、無 key）：開啟後整理生效、關閉引擎無孤兒程序、模型下載可取消 |
| **2** | `cleanup_eval.jsonl` + 品質閘跑第一輪、規則層 app profile、結構化擴充、風格字典（預設關） | Phase 1 | 品質閘三指標記錄在本檔；§4.6 決定 embedded 是否預設開啟 |

**Phase 1 完成前，`embedded` 不寫進 README 的功能清單**——沒到手的東西不宣傳（Hard Constraint #17）。

---

## 8. 風險與待驗證

| # | 項目 | 狀態 |
|---|---|---|
| 1 | Qwen3-0.6B 繁中整理品質 | **未驗證**，品質閘決定 |
| 2 | 無 GPU 筆電上 0.6B 的實際延遲 | **未驗證**（本機 22 核不代表目標機器） |
| 3 | `llama-server --api-key` 參數的版本相容性 | **待驗證** |
| 4 | llama-server.exe + DLL 的打包體積與 PyInstaller 相容性 | **待驗證** |
| 5 | 防毒對「安裝檔內含會開本機 server 的 exe」的反應 | **待驗證**（README 防毒預告段落需同步更新） |
| 6 | Job Object 綁定在 per-user 權限下的行為 | **待驗證** |
