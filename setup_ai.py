# -*- coding: utf-8 -*-
"""設定「整理」功能要用哪個 AI — 不用編 JSON、不用開終端機打指令。

用法：雙擊 設定整理AI.bat，或 python setup_ai.py

「整理」是可選的第二層：去掉「嗯、那個」、補標點、你講到一半改口只留最後版本。
**沒有設定也能用**——第一層本機規則永遠會跑，只是比較陽春。

🔐 金鑰處理：
   輸入時不會顯示在畫面上，也不會寫進任何檔案或 log。
   直接寫進 Windows 使用者環境變數（登錄檔），不經過命令列參數，
   所以不會出現在工作管理員的命令列欄位裡。
"""
import ctypes
import getpass
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

PROVIDERS = [
    ("gemini", "Google Gemini", "GEMINI_API_KEY", "https://aistudio.google.com/apikey",
     "只要 Google 帳號，申請最簡單。免費層 flash-lite 500 次/天（2026-07 實測）"),
    ("nvidia", "NVIDIA NIM", "NVIDIA_API_KEY", "https://build.nvidia.com/",
     "有免費額度，本專案預設。實測整理一句約 1.7-2.6 秒"),
    ("groq", "Groq", "GROQ_API_KEY", "https://console.groq.com/keys",
     "免費層速度最快的一批（2026-07 查得約 30 次/分）"),
    ("cerebras", "Cerebras", "CEREBRAS_API_KEY", "https://cloud.cerebras.ai/",
     "免費日額度最寬鬆（2026-07 查得約 100 萬 token/天）"),
    ("sambanova", "SambaNova", "SAMBANOVA_API_KEY", "https://cloud.sambanova.ai/",
     "免綁卡。⚠️ 各模型限額差異大（部分僅 20 次/天，以官網為準）"),
    ("openrouter", "OpenRouter", "OPENROUTER_API_KEY", "https://openrouter.ai/keys",
     "一把金鑰通到約 30 個免費模型"),
    ("mistral", "Mistral", "MISTRAL_API_KEY", "https://console.mistral.ai/",
     "額度最寬（查得約 10 億 token/月）。⚠️ 註冊要手機簡訊驗證"),
]


def set_user_env(name, value):
    """寫進 HKCU\\Environment 並廣播變更。

    不用 setx：那會把金鑰放進命令列參數，工作管理員看得到。
    """
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0,
                        winreg.KEY_SET_VALUE) as k:
        winreg.SetValueEx(k, name, 0, winreg.REG_SZ, value)
    # 通知其他程式環境變數變了（不通知的話要登出重登才生效）
    HWND_BROADCAST, WM_SETTINGCHANGE, SMTO_ABORTIFHUNG = 0xFFFF, 0x001A, 0x0002
    ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, ctypes.c_wchar_p("Environment"),
        SMTO_ABORTIFHUNG, 3000, None)
    os.environ[name] = value          # 讓本次測試立刻讀得到


def status():
    print("=" * 62)
    print("  目前的「整理」設定")
    print("=" * 62)
    try:
        import dictate as D
        cands = D._candidates()
        if not cands:
            print("  ⚠️  目前沒有可用的 AI，整理只會做本機規則清理")
        for i, (name, url, model, key) in enumerate(cands, 1):
            where = "本機" if "localhost" in url or "127.0.0.1" in url else "雲端"
            print(f"  {i}. {name:<11} {model:<38} {where}")
        print("\n  （由上往下試，前一個不能用就換下一個）")
    except Exception as e:
        print(f"  讀不到設定：{str(e)[:80]}")
    print()


def pick_local():
    print("\n── 本機 AI（Ollama）──────────────────────────────────")
    print("  最推薦：完全免費、沒有次數限制、**文字也不會離開你的電腦**。")
    print("  你的顯卡如果還有空間，整理逐字稿用 4B 等級的小模型就夠了。\n")
    import shutil
    if shutil.which("ollama"):
        print("  ✅ 偵測到已安裝 Ollama。接下來在終端機執行一次：\n")
        print("       ollama pull qwen3:4b\n")
        print("  拉完就好，口述引擎會自動接上（重開一次引擎）。")
    else:
        print("  ❌ 還沒安裝。三步：")
        print("     1. 到 https://ollama.com/ 下載安裝")
        print("     2. 開終端機執行： ollama pull qwen3:4b")
        print("     3. 重開口述引擎，它會自動偵測到")
    print("\n  設定檔不用改——providers 清單第一筆就是本機。")


def pick_cloud(idx):
    name, label, env, url, note = PROVIDERS[idx]
    print(f"\n── {label} ──────────────────────────────────")
    print(f"  {note}")
    print(f"  申請免費金鑰：{url}\n")
    print("  🔐 等一下貼上金鑰時畫面不會顯示（正常現象），")
    print("     金鑰只會寫進你自己的 Windows 使用者環境變數，")
    print("     不會寫進任何檔案，也不會出現在紀錄裡。\n")
    key = getpass.getpass("  貼上金鑰後按 Enter（直接 Enter 可取消）： ").strip()
    if not key:
        print("  已取消，沒有變更任何設定。")
        return
    try:
        set_user_env(env, key)
    except Exception as e:
        print(f"  ❌ 寫入失敗：{str(e)[:100]}")
        return
    print(f"  ✅ 已設定 {env}（長度 {len(key)} 個字元，內容不顯示）")
    test()


def test():
    print("\n  測試中…")
    try:
        import importlib
        import dictate as D
        importlib.reload(D)
        raw = "嗯今天我把那個報價單改好了嗯就是說 明天要處理維護的事情 啊不對 是這禮拜"
        out = D.polish(raw, None)
        print(f"\n  原文：{raw}")
        print(f"  整理：{out}")
        if out.strip() == raw.strip():
            print("\n  ⚠️  結果跟原文一樣，可能沒接上。看 dictate.log 有沒有錯誤訊息。")
        else:
            print("\n  ✅ 整理有生效。重開口述引擎就會開始用了。")
    except Exception as e:
        print(f"  ❌ 測試失敗：{str(e)[:150]}")


def main():
    print()
    status()
    print("  想做什麼？\n")
    print("   1. 用本機 AI（最推薦：免費、無限制、文字也不出網）")
    for i, (_, label, env, _, note) in enumerate(PROVIDERS, 2):
        mark = "已設定 ✅" if os.environ.get(env) else "未設定"
        print(f"   {i}. 設定 {label:<12}（{mark}）")
    print("   t. 測試目前的設定")
    print("   x. 完全關閉整理（只用本機規則清理）")
    print("   q. 離開\n")
    c = input("  輸入編號： ").strip().lower()

    if c == "1":
        pick_local()
    elif c.isdigit() and 2 <= int(c) <= 1 + len(PROVIDERS):
        pick_cloud(int(c) - 2)
    elif c == "t":
        test()
    elif c == "x":
        import json
        cfg = Path(__file__).resolve().parent / "config.json"
        if os.environ.get("LOCALAPPDATA"):
            alt = Path(os.environ["LOCALAPPDATA"]) / "local-dictate" / "config.json"
            if alt.exists():
                cfg = alt
        if cfg.exists():
            j = json.loads(cfg.read_text(encoding="utf-8-sig"))
            j.setdefault("polish", {})["enabled"] = False
            cfg.write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"\n  ✅ 已關閉整理（{cfg}）。第一層本機清理照常運作。")
        else:
            print("\n  找不到設定檔，先啟動一次口述引擎再回來。")
    else:
        print("\n  沒有變更。")
    print()


if __name__ == "__main__":
    main()
    input("按 Enter 關閉…")
