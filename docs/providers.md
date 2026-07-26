# 整理層要接哪一家

> 這份只影響「**整理**」那一層（去口頭禪、補標點）。
> **語音辨識永遠在本機跑，跟這份文件無關**——不管你接哪一家，聲音都不會出網。

整理分兩層：

| 層 | 需要什麼 | 出網？ |
|---|---|---|
| **第一層：本機規則清理** | 什麼都不用 | ❌ |
| **第二層：LLM 整理**（可選） | 一個 OpenAI 相容端點 | ⚠️ 只送「已轉好的文字」 |

**第一層永遠會跑。** 就算你完全不設定第二層，語助詞（嗯／呃／對對對）跟重複字還是會被清掉。第二層處理的是需要理解語意的部分——例如你講到一半改口，只留最後的版本。

---

## 最推薦：本機 LLM（完全免費、無速率限制、不出網）

如果你的顯卡還有空間，這是最好的選擇：**沒有額度、沒有速率限制、文字也不出網**，把最後一個隱私缺口補掉。

whisper 的 `medium` 模型大約佔 1GB VRAM，所以 6GB 的卡還有約 5GB 可以放一個小 LLM。

### Ollama（最簡單）

1. 裝 [Ollama](https://ollama.com/)
2. 拉一個小模型（整理逐字稿不需要大模型，4B 等級就夠）：
   ```bash
   ollama pull qwen3:4b
   ```
3. 完成。`config.json` 的預設 provider 清單第一筆就是它，會自動被用到。

沒裝也不會有事——連不上會被記起來，那次啟動不再重試，直接往下一家走。

### LM Studio

開 server 之後把 `config.json` 裡 local 那筆的 `url` 改成 `http://localhost:1234/v1/chat/completions`，`model` 換成你載入的模型名稱。

---

## 雲端免費方案

⚠️ **免費額度變動很快，下面的數字請以各家官網為準。** 本表整理於 2026-07，來源附在最後。

| 供應商 | 免費額度（2026-07 查得） | 需要 | 備註 |
|---|---|---|---|
| **NVIDIA NIM** | 有免費額度 | `NVIDIA_API_KEY` | **本專案預設**。實測 `openai/gpt-oss-120b` 約 1.7–2.6 秒 |
| **Groq** | 約 30 RPM／1,000 RPD | `GROQ_API_KEY` | 自研 LPU，速度是免費層裡最快的一批 |
| **Cerebras** | 約 100 萬 token／天 | `CEREBRAS_API_KEY` | 日額度最寬鬆 |
| **OpenRouter** | 約 20 RPM，免費模型每日有上限 | `OPENROUTER_API_KEY` | 一把 key 通到約 30 個免費模型 |
| **Google Gemini** | 約 10–15 RPM（Flash） | `GEMINI_API_KEY` | 端點不是標準 OpenAI 格式，要改 `url` 用相容層 |

上面四家 `config.json` 裡都已經預先填好了，**你只要設對應的環境變數就會自動被用到**，不用改設定檔。

### 設環境變數（Windows）

```powershell
setx GROQ_API_KEY "你的key"
```

設完**要重開口述引擎**才會讀到。

⚠️ 不要把 key 寫進 `config.json`——那個檔案雖然在 `.gitignore` 裡，但一旦有人手動 commit 就外流了。用環境變數。

---

## 順序怎麼決定

`config.json` 的 `polish.providers` 是一個清單，**由上往下試**，規則：

- `key_env` 有填、但環境變數不存在 → **直接跳過**（不浪費一次連線）
- localhost 連不上 → 記起來，**那次啟動不再重試**
- 回應異常膨脹（超過原文 1.5 倍 + 40 字）→ **丟棄，改用原文**（防止模型把你的口述當成指令執行，見 `references/pitfalls.md` 第 3 條）

想調順序就直接改清單順序。

### 想完全不出網

兩個做法，選一個：

1. `polish.providers` 只留 local 那一筆
2. `polish.enabled` 設 `false`（第一層本機清理照常運作）

或者臨時性地——**把面板上的 `✨整理` 點成灰色**，那一次就純本機。

---

## 資料來源

免費額度整理自以下比較文章（2026-07 查得，數字會變，以官網為準）：

- [Free LLM API in 2026: 13 Options Ranked and Compared — OpenRouter](https://openrouter.ai/blog/tutorials/free-llm-apis-compared/)
- [Best Free LLM API Tiers in 2026: Groq, Cerebras, GitHub Models & More](https://wetheflywheel.com/en/ai-model-access/free-llm-api-tiers-2026/)
- [Free LLM APIs in 2026: 13 Providers Compared](https://klymentiev.com/blog/free-llm-api)
