# SPEC：整理層（對標 Typeless）

> 這份同時是 SDD（設計文件）與驗收規格。狀態：**v2，2026-07-28**。
> v1 經對抗式審查（外部獨立審查者，結論 4/10・拒絕進 Phase 1）後全面改版；
> 審查抓到的核心矛盾與修正一覽見 §9 審查紀錄。
> 讀者：要動 `polish()` / `tidy_local()` 相關程式碼的人。動手前先讀 `references/pitfalls.md` 第 3 條。

---

## 0. 一句話問題陳述

**「整理」的 LLM 層對下載安裝檔的人來說目前不存在。**

`_candidates()`（`dictate.py`）的每一條路都有前置條件：

| provider | 前置條件 | 下載 exe 的一般使用者有嗎 |
|---|---|---|
| local（ollama） | 自己裝 Ollama + 拉模型 | ❌ |
| 雲端七家（nvidia/groq/cerebras/gemini/sambanova/openrouter/mistral） | 自己申請 key + 設環境變數 | ❌ |

兩者皆無 → `polish()` 直接回原文，只剩第一層規則清理。
Typeless 的招牌體驗（**改口只留最後版本**、通順化、語意級標點）出廠時缺席。

### 目標的誠實版本（v2 修正）

v1 寫「零設定、零出網、出廠即可用」——**自相矛盾**：模型要下載（出網一次）、要有人按下開啟（一次設定）。改為：

> **一次明示下載之後，日常零設定；音訊與逐字稿永不出機。**

遠期可另出「Full Offline 安裝包」（含整理模型）給完全離線環境，Lite 包維持現狀。

---

## 1. 對標 Typeless：差距總表

（同 v1，狀態更新）

| 能力 | Typeless | 我們 | 處置 |
|---|---|---|---|
| 語音辨識 | 雲端（音訊上傳） | ✅ 本機 | 不動 |
| 費用／額度 | 8,000 字/週免費，$12-30/月 | ✅ 免費無上限 | 不動 |
| 去口頭禪 | ✅ | 🟡 規則層有 | Phase 1 補 LLM 級 |
| **改口只留最後版本** | ✅ | ❌ | **Phase 0 規則版（新）→ Phase 1 LLM 版** |
| 智慧結構化 | ✅ | 🟡 只插換行 | Phase 2 擴充規則；不用 LLM |
| 依 app 調語氣 | ✅ | 🟡 `app_styles` v1 | Phase 2 下放到規則層 |
| 個人字典 | ✅ | ✅ `vocab.txt` | 不動 |
| 學個人書寫風格 | ✅ | ❌ | Phase 2（剪貼簿 diff，預設關） |
| 免費 API 入口 | —（它就是雲端服務） | ✅ **已做**：8 家 provider 鏈 + `設定整理AI.bat` | 已交付（2026-07-28） |
| 翻譯／語音改寫指令／手機鍵盤 | ✅ | ❌ | 不做／不做／遠期 PWA |

---

## 2. 核心架構修正（v2）：改口處理不交給 LLM 自由改寫

審查的關鍵洞見：**「改口只留最後版本」本質上是刪除操作**，不需要允許 0.6B 模型重寫整段文字。v2 把管線改成：

```
ASR 文字
  → ① 確定性改口剖析器（correction-span parser，規則）        ← Phase 0，新
       偵測「不對/不是/我是說/改成/應該是/等等」等標記，
       標出【撤回區】與【最後版本】，撤回區直接刪除
  → ② tidy_local()（既有規則清理：口頭禪/重複字/標點/條列）
  → ③（可選）LLM 層：兩種模式
       edit-plan 模式（目標）：不可變 span 換成 sentinel，LLM 只回
         delete/keep/標點 的編輯計畫，程式套回原文
       rewrite 模式（過渡）：現行整段改寫，套 guard v2
  → ④ guard v2 驗證（基準 = ①處理後的文字，不是原始 ASR）
```

### 2.1 Guard v2（修正 v1 的自相矛盾）

v1 的錯：以**原始 ASR 文字**當基準抽 protected token → 被使用者自己撤回的「3000」也被保護 → 正確整理必被拒。

v2 規則：
- **基準是 ① 改口剖析之後的文字**。被撤回的數字/專名不在保護清單。
- 保護清單：數字串、URL、Email、英文 token、`vocab.txt` 詞條、**否定與範圍詞**（不、不要、取消、最多、至少）。
- **數值表面形式視為不可變**：「三千」→「3000」、「3,000」→「3000」、`7/28`→「7 月 28 日」都算違規（正規化屬確定性層的工作，不給 LLM 做）。中文數字也要進抽取器，否則「三千」根本沒被保護。
- 除存在性外，驗證**次數與相對順序**（防「維護費 3000、訂金 5000」被調換、防重複數字被刪一個）。
- 大小寫修正（iphone→iPhone）與全半形屬確定性 canonicalize 的工作（已存在），guard 對這類差異用 NFC ＋ casefold 後比對，不誤殺。
- 任何違規 → 丟棄 LLM 結果、回 ② 的輸出，log 記 `guard_tripped`＋**違規類型與位置，不記實際值**（電話/金額不落地，見 §5 log 政策）。

已知殘餘風險（誠實列出）：guard 擋不住「刪掉語意詞但不在保護清單」的改寫。這是 rewrite 模式的固有缺陷，也是要走 edit-plan 模式的理由。

---

## 3. Sidecar v2（llama-server）

### 3.1 狀態機（v1 缺，8s/10s 矛盾由此解）

```
STOPPED → STARTING → READY ⇄ BUSY
                       ↓ (llama-server 內建 idle sleep)
                     SLEEPING（程序在、模型已卸載）
任何狀態 → STOPPING → STOPPED
啟動失敗/崩潰 → BACKOFF（限次重啟、指數退避）→ DEAD（本場放棄）
```

- 單一 spawn lock；`ensure()` 併發呼叫只允許一個進 STARTING，其餘等或直接 fallback。
- process generation ID：readiness 與請求都帶 generation，殺舊拉新時不會把舊程序的回應當新的。
- `active_requests` 計數：STOPPING 前等 in-flight 清空。
- 多開防護：主程式已有具名 mutex 單一實例鎖，sidecar 埠檔（`%LOCALAPPDATA%\local-dictate\sidecar.lock`）記 PID＋port＋generation。

### 3.2 生命週期要點（採審查修正）

- **spawn 順序**：`CreateProcess(CREATE_SUSPENDED)` → `AssignProcessToJobObject` → 成功才 `ResumeThread`，失敗立即 terminate。Job handle 不可繼承、由主程序單一持有。消除「assign 前父死→孤兒」的空窗。需測 Task Manager 強殺父程序、以及主程序已在外層 Job 的巢狀情境。
- **閒置卸載不自己殺程序**：用 llama-server 的 `--sleep-idle-seconds`（程序常駐、模型與 KV cache 卸載、新請求自動重載；`/health` 不會喚醒）。Job Object 只負責「主程序死亡時的最終清理」。（⚠️ 此參數引自 llama-server 官方 README，**版本相容性實作時要驗**。）
- **timeout 要能終止生成**，不是只放棄等待：`--parallel 1`、`max_tokens` 硬上限、總請求 deadline（不是每家各等一次）；timeout 後驗證 HTTP disconnect 是否釋放 slot，不能釋放就整個 sidecar 重啟（走 BACKOFF）。
- **埠與歸屬**：不預找空埠（TOCTOU），直接讓 server bind、失敗換埠重試；readiness = child PID 存活 ＋ **帶 API key 打 `/v1/models` 驗回 alias**（`/health` 是公開端點不驗 key，200 不代表那是自己的 server）。啟動帶唯一 `--alias`。
- **安全參數**：`--api-key-file`（**不用 `--api-key <值>`**——值會出現在命令列，跟 dispatch 的教訓同一顆雷）、`--no-ui`、`--offline`、`--log-disable`（或有上限的去識別 stderr ring buffer）。stdout/stderr 若接 PIPE 必須持續 drain，否則塞滿會讓 child 卡死。
- **模型執行設定全部釘死**（否則延遲與輸出不可重現）：llama.cpp binary SHA、GGUF revision SHA、chat template、`enable_thinking=false`（Qwen3 預設可能開 thinking）、sampling 參數與 seed、context/threads/batch/parallel/max_tokens、prompt 版本。

### 3.3 隱私模式（v1 重大遺漏）

v1 的 fallback 鏈會讓「選了本機 AI」的使用者在 sidecar 崩潰時**不知情地把逐字稿送上雲端**。v2 新增 `polish.privacy_mode`：

| 模式 | 行為 |
|---|---|
| `local_only` | embedded/ollama 失敗 → 直接規則層，**永不出網**。選「本機 AI」時預設此值 |
| `cloud_primary` | 使用者指定一家雲端為主力；失敗 → 規則層（**不**瀑布式試完全部——每句最多一次雲端嘗試，守延遲預算） |
| `cloud_fallback_allowed` | 明示同意後才允許跨 provider 備援（現行行為，維持給已理解的使用者） |

`設定整理AI.bat` 選「本機 AI」時寫入 `local_only`；選雲端家時寫入 `cloud_primary`。現行預設（Jason 型使用者）維持 `cloud_fallback_allowed` 相容。

---

## 4. 品質閘 v2（先於 Phase 1 出貨，不是 Phase 2）

v1 的閘可以被「原文照抄」滿分通過——不變量全過≠有整理。v2 拆五組指標：

| 指標 | 門檻 |
|---|---|
| 安全不變量（保護 token/否定詞/長度） | 被接受的輸出 **100%** 通過（determinstic，不是 90%） |
| **核心任務成功率**：撤回區確實刪除、最後版本保留 | ≥90%（初值，修訂要留紀錄，不做移動球門） |
| guard 誤殺率（正常整理被拒） | 明確量測並回報，含 FP/FN |
| fallback／timeout 率 | 明確量測並回報 |
| 人工盲評（語意保真/流暢/過度刪除） | 抽樣，出貨前至少一輪 |

- 測試集：主集 30-50 句＋**holdout**（不用於調 prompt）；涵蓋改口、口頭禪、金額、人名、URL、否定詞、LINE 短句、長段落。
- 延遲報 warm/cold 各 p50/p95、timeout 率、峰值 RAM、**ASR＋LLM 同時運作**時的延遲；標明最低支援硬體，不只 22 核開發機。
- **CI 不需要真模型也能測生命週期**：fake `llama-server.exe` 驗父強殺/重複 ensure/埠衝突/請求中 idle/timeout 殘留/crash-backoff/Job 繼承/下載取消/磁碟滿/hash 錯——全部進自動化。真模型品質跑 release gate（本機手動）。

---

## 5. Log 政策（配合 guard）

`dictate.log` 既有原則不變（只記前 40 字）。guard 相關新增：**不記實際的電話/金額/URL 值**，只記類型、位置、不可逆摘要。

---

## 6. 免費 API 入口（已交付，2026-07-28）

provider 鏈現況：`local → nvidia → groq → cerebras → gemini → sambanova → openrouter → mistral`＋`設定整理AI.bat` 互動選單。額度數字與待驗證標註見 `docs/providers.md`。

審查意見的採納狀態：
- ✅ Gemini 值得加（flash-lite；免費層內容可能被 Google 用於改善產品——已屬「文字出網」的既有告知範圍）
- ✅ SambaNova 官方表列多數模型 20 RPD → 已在文件標示、放鏈的後段。**保留在鏈中是使用者決策**（免綁卡、沒 key 就跳過零成本）
- ⏸ Cloudflare Workers AI：OpenAI 相容端點存在但要 account_id＋scoped token，設定摩擦高於受眾承受度，暫不加，記錄於此
- ✅ 瀑布延遲問題 → 併入 §3.3 privacy_mode（cloud_primary 每句最多一次雲端嘗試）

---

## 7. 明確不做（v1 不變）

翻譯、語音改寫指令、LLM 結構化、強制 Ollama、雲端帳號體系。理由同 v1。

---

## 8. 交付切分（v2 重排）

| Phase | 內容 | 驗收 |
|---|---|---|
| **0**（純規則，立即有使用者價值） | ① 確定性改口剖析器（「不對/我是說/改成…」撤回刪除）② guard v2 骨架（以剖析後文字為基準；含中文數字抽取、次序驗證）③ `privacy_mode` 設定與 `polish()` 總 deadline | 剖析器測試案例進 CI（含「維護費 3000 不對 5000」）；guard FP 率在現有 nvidia provider 實測 |
| **1** | sidecar v2（狀態機＋suspended-spawn Job＋sleep-idle＋authed readiness）；fake-server 生命週期 CI；**品質閘跑完才出貨**；先 rewrite 模式＋guard v2 | §4 五指標達標；乾淨機器無 key 無 ollama 可用；父強殺無孤兒 |
| **2** | edit-plan 模式取代 rewrite；風格字典（預設關）；規則層 app profile；結構化擴充 | edit-plan 在 holdout 上核心任務成功率 ≥ rewrite 模式 |

**Phase 1 完成前，embedded 不寫進 README 功能清單**（Hard Constraint #17）。

---

## 9. 審查紀錄（audit trail）

- **2026-07-28**：v1 由外部獨立審查者做對抗式審查，結論 **4/10・拒絕進 Phase 1**。
  成立且已採納：guard 與改口功能互斥（→§2）、Job assign 空窗（→§3.2）、無狀態機（→§3.1）、
  自殺式 idle unload（→sleep-idle）、timeout 不終止生成、埠 TOCTOU＋`/health` 不驗 key、
  8s/10s 矛盾、`--api-key` 上命令列、Qwen3 thinking 未釘死、**privacy fallback 漏洞**（→§3.3）、
  品質閘可被照抄通過（→§4）、瀑布延遲。
  未採納：移除 SambaNova（使用者明示保留，文件已標限額）；`gemini-2.5-flash-lite` 命名
  （審查者引的是舊文件；本機 AI Studio 頁 2026-07-27 實測為 3.1 系列）。
- 待驗證清單：`--sleep-idle-seconds`/`--api-key-file`/`--offline` 的版本相容性、
  Qwen3-0.6B 繁中品質、無 GPU 筆電延遲、llama-server 打包體積、防毒反應、巢狀 Job 行為。
