# Roadmap

> 這份不是願景，是**待辦清單**。做完一項就打勾，順序依「使用者感受到的改善 ÷ 實作成本」。
> 排序依據來自 2026-07-26 的一次三方研究（工程發行／使用者流失點／onboarding 設計），
> 結論交叉查核過，數字用本機實測修正過（見下方「查核紀錄」）。

## 核心判斷

> 功能已經夠了。**死在路上的是「進場」和「敢用」。**

現況是：用工程師的發貨方式（GitHub + `pip install`），去服務非工程師的需求。
最大的流失不在辨識率，在使用者根本走不到能講第一句話的地方。

---

## P0 · 一鍵安裝檔 ✅ 已發佈（v0.1.0 / v0.1.1）

**目標**：使用者只下載一個 `local-dictate-setup.exe`，不需要 Python、Git、終端機，
而且**不用網路就能完成第一次聽寫**。

- [x] PyInstaller `--onedir --windowed` 打包（**不要**先追求 onefile）
- [x] Inno Setup 安裝器，`PrivilegesRequired=lowest`（per-user，不跳 UAC）
- [x] 安裝器內含 `base` 模型（141MB），首次啟動零下載
- [x] 資料寫在 `%LOCALAPPDATA%\local-dictate\`，不要寫進安裝目錄
- [x] 固定 `AppId`，升級覆蓋而不是裝出第二份
- [x] 解除安裝時**詢問**是否保留模型與字典，不要默默刪掉幾 GB
- [x] 乾淨機驗證 → 做成 **CI 常設 job**（`verify-install`，2026-07-29）：
  另一台乾淨 runner 只拿安裝檔 artifact（不 checkout、不裝相依）→ 靜默安裝 →
  啟動 45 秒驗五項斷言（程序存活/模型載入/零下載承諾/熱鍵註冊/設定落位）→
  靜默解除安裝驗清乾淨。**每次 release 自動跑。**
  （開發機 Windows 11 家用版不支援 Sandbox，CI 路線反而更好——可重複）
- [ ] **仍驗不到、需要實機的**：麥克風實錄、實際貼上、GPU。目前靠使用者回報
  （Issue #1）＋ Jason 自己這台

**實裝驗證紀錄（2026-07-26，在開發機上）**：下載 → SHA256 校驗相符 → 靜默安裝 exit 0
（245MB／1172 檔）→ 內建 base 落在正確位置 → 執行 → 靜默解除安裝 exit 0、目錄清乾淨。
過程中抓到「首次啟動選了沒內建的模型」，已於 v0.1.1 修正。

## P0.5 · 出廠品質（2026-07-29 完成）

- [x] **背景模型升級**：出廠 base 只是「首啟零下載」的起點——啟動後背景下載
  這台硬體值得的模型（GPU→medium／CPU 8核+→small），worker 空檔熱切換，
  面板通知。`auto_upgrade_model` 可關。修掉「出廠預設是自己標不建議的模型」問題

## P0 · GitHub Actions 自動出 release ✅

- [x] `windows-latest` runner：鎖版本 → 跑測試 → build onedir → build installer → 出 SHA256 → 上傳 release
- [x] 公開 repo 用標準 runner 不計費
- [x] 32 項純函式測試（含「熱鍵不可以是 Alt+Space/Enter」的回歸測試）

⚠️ 麥克風、熱鍵、GPU **CI 測不到**，仍需實機驗證。

**已知要處理的打包坑**（來自 codex 的評估）：
`ctranslate2` 的 `.pyd`/DLL、`av`/FFmpeg DLL、`sounddevice`/PortAudio DLL、
Tk/Tcl 資料目錄、OpenCC 字典資料、CA certificate bundle。**關閉 UPX**（會增加防毒誤判）。
`--windowed` 之後沒有 console，啟動錯誤必須跳 GUI 視窗而不是靜默死掉。

## P0 · GitHub Actions 自動出 release

- [ ] `windows-latest` runner：鎖版本 → 跑測試 → build onedir → build installer → 出 SHA256 → 上傳 release
- [ ] 公開 repo 用標準 runner 不計費

⚠️ 麥克風、熱鍵、GPU **CI 測不到**，仍需實機驗證。

## P1 · 首次啟動精靈

把 `doctor.py` / `tune.py` 藏進去，使用者不該需要知道它們存在。

- [ ] 環境檢查（Windows x64 / 寫入權限 / 空間 / 原生 DLL 能不能載入）
- [ ] 麥克風：列裝置 → 音量表 → **錄 3 秒放給他聽**；權限關著就給按鈕直接開 Windows 設定
- [ ] 熱鍵：實際呼叫 `RegisterHotKey`，衝突就當場讓他按新的
- [ ] 模型：驗證內附 base 的 hash
- [ ] **教學測試在程式自己的文字框完成**——避開「焦點不在輸入框」那一整類問題
- [ ] 選配才問：開機啟動、背景下載 small、本機智慧整理
- [ ] `tune.py --bench` 移到背景或設定頁，不要卡在首次體驗前面

## P1 · 模型管理器

- [ ] `base` 內建即用 → `small` 背景升級 → `medium` 明確選配
- [ ] 下載器：總大小／進度／速度／暫停／取消／重試
- [ ] 下載到 `.part` → 驗 SHA256 → atomic rename
- [ ] 升級失敗不影響現有可用模型
- [ ] 設定頁可看佔用空間、切換、刪除

## P2 · 面板再簡化

- [x] `📋` 按鈕：一鍵複製最後結果（解決「游標沒點進輸入框 → 字印不出來」）
- [x] app 名稱白話化（`WINWORD.EXE` → 📄 Word、`LINE.exe` → 💬 LINE）
- [x] 錄音時顯示目標視窗 ＋ 即時音量條
- [x] `✕` 兩段式確認，避免手滑關掉
- [x] 面板直接標示快捷鍵（使用者不會知道有熱鍵，除非面板自己講）
- [x] 每 2 秒重新宣告最上層（不然被壓到底層就再也叫不回來）
- [x] 提示音改成合成正弦音＋包絡（方波沒有包絡＝刺耳的「滴滴嘟嘟」）
- [ ] 三色狀態邊框（待命灰／錄音紅脈動／轉寫藍）
- [ ] 首次啟動精靈（見 P1）

## P2 · 整理層（零成本趨近 Typeless）

> 📐 完整設計與驗收規格：**[docs/SPEC-cleanup.md](docs/SPEC-cleanup.md)**（2026-07-28）。
> 核心診斷：LLM 整理層對下載 exe 的人**目前不存在**（要嘛要 ollama 要嘛要 API key），
> 解法＝內嵌 llama-server sidecar ＋ 程式端三道防線 ＋ 品質閘。以 SPEC 為準，本節只是索引。

- [x] 第一層本機規則：語助詞、重複字、標點正規化（零設定、0 延遲、不出網）
- [x] 「第一…第二…」自動分行（**只插換行、不改字**）
- [x] 依目標 app 換整理風格
- [ ] 內嵌 `llama-server.exe` sidecar（只監聽 127.0.0.1、隨機 port），使用者開啟才下載模型
- [ ] 保護 token：整理前後比對數字／網址／Email／字典詞，任一被改動就退回規則版
- [ ] 「原文／整理後」快速切換

⚠️ **不要強制安裝 Ollama**。已裝的人自動接（現在就會），沒裝的人給內嵌 sidecar。
理由：Ollama 是另一個背景程式與更新週期，會讓解除安裝與支援責任變複雜。

## P3 · Microsoft Store（MSIX）

零預算下**唯一**能真正消掉 SmartScreen 警告並拿到自動更新的路線（Store 代簽）。
Inno 版穩定之後再轉，且要保留直接下載版。

- [ ] 實測 `RegisterHotKey`、開機啟動、麥克風 capability、full-trust、下載模型到 app data
- [ ] 「所有 Windows 設定下都能不登入帳號安裝免費 Store App」— **待驗證**

## P3 · GPU 加速包（Beta）

- [ ] 偵測到相容 NVIDIA GPU 才顯示，明講要多下載約 1.9GB
- [ ] 版本完全鎖定，載入失敗立刻退 CPU 不崩潰
- [ ] NVIDIA 套件是 proprietary license，**能不能重新打包進安裝器要另外確認**

## P4 · macOS

轉寫核心本來就跨平台，缺的是 OS 整合層。對照表在 [docs/macos.md](docs/macos.md)。
**最缺的是 Mac 實機數字**——見 [issue #1](../../issues/1)。

## 明確不做

- PyInstaller `--onefile`（每次啟動解壓、防毒干擾、除錯困難）
- embeddable Python + 手工 Tcl/Tk（官方 embeddable 不含 Tcl/Tk 與 pip，工程量不比 PyInstaller 小卻沒有使用者價值）
- `pipx`（本身就要求 Python 3.10+ 與 pip，沒有解決核心摩擦）
- Scoop（目標使用者沒裝）
- 強制安裝 Ollama

這些看起來能縮短指令，但沒有縮短「從下載到第一次成功貼上文字」的距離。

---

## 查核紀錄

三方研究的數字用本機實測修正過：

| 項目 | 外部 AI 說 | 本機實測 | 處置 |
|---|---|---|---|
| CUDA 三件套大小 | 約 1.2GB（PyPI 下載檔） | **1,926MB**（裝完佔用） | 採用實測值。使用者感受的是磁碟佔用 |
| tiny / base 模型 | 75MB / 148MB | 74.6MB / 141.0MB | 一致 |
| 首發要內建哪個模型 | agy 說 tiny、codex 說 base | — | **採 base**。本機 benchmark 顯示 base 已會把英文品牌名聽成不相干中文，tiny 只會更糟 |
| 「regex 條列化可覆蓋 70% 需求」 | agy | 無出處 | **刪除**，不採用未經驗證的百分比 |
