# -*- coding: utf-8 -*-
"""不需要麥克風／GPU／視窗的純函式測試。CI 跑這支。

這裡的每一條都對應一個真的踩過的坑，不是形式測試：
  · 清理規則誤刪內容 → 使用者的話被改掉，而且不會發現
  · 條列分行改到字 → 同上
  · 熱鍵字串解析不出來 → 使用者拿到一個「按了沒反應」的版本
  · app 名稱對照壞掉 → 面板顯示執行檔名，非工程師看不懂

用法：python tests/test_pure.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import dictate as D          # noqa: E402

fails = []


def check(name, got, want):
    if got == want:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name}\n       got  {got!r}\n       want {want!r}")
        fails.append(name)


def check_true(name, cond, detail=""):
    if cond:
        print(f"  ok   {name}")
    else:
        print(f"  FAIL {name} {detail}")
        fails.append(name)


print("[本機清理] 該刪的")
check("句首語助詞", D.tidy_local("嗯今天我把報價單改好了"), "今天我把報價單改好了")
check("夾在逗號中間", D.tidy_local("我改好了，嗯，然後發了一篇"), "我改好了，然後發了一篇")
check("就是說", D.tidy_local("就是說我覺得可以"), "我覺得可以")
check("連續重複字", D.tidy_local("我我我覺得可以"), "我覺得可以")

print("\n[本機清理] 絕對不能被動到的（誤刪比留著糟糕得多）")
check("『那個』是實詞", D.tidy_local("那個檔案我改好了"), "那個檔案我改好了")
check("『然後』是連接詞", D.tidy_local("然後我就把它關掉了"), "然後我就把它關掉了")
check("『就是』是實詞", D.tidy_local("就是這個問題"), "就是這個問題")
check("正常句不動", D.tidy_local("我想想看"), "我想想看")
check("英文品牌名不動", D.tidy_local("easyknowai 的報價單"), "easyknowai 的報價單")

print("\n[條列分行] 只插換行、一個字都不能改")
src = "我覺得有三個重點第一是速度第二是準確度第三是隱私"
out = D.tidy_local(src)
check_true("三個序數會分行", "\n" in out, out)
check("分行後字元完全相同", out.replace("\n", ""), src)

src2 = "第一點先確認麥克風第二點再檢查權限"
out2 = D.tidy_local(src2)
check_true("句首序數也要算數量", "\n" in out2, out2)
check("句首序數不加前導換行", out2.replace("\n", ""), src2)

check("單一序數不動 A", D.tidy_local("第一次用的時候覺得很難"), "第一次用的時候覺得很難")
check("單一序數不動 B", D.tidy_local("這是第一版，我們之後會改"), "這是第一版，我們之後會改")

print("\n[改口剖析] 該改的（SPEC-cleanup v2 §2）")
check("數字改口（正典案例）",
      D.correct_local("維護費 3000，不對，改成 5000"), "維護費 5000")
check("數字改口（ASR 空格風）",
      D.correct_local("維護費 3000 不對 是 5000"), "維護費 5000")
check("片語改口（共同結尾+動詞錨點）",
      D.correct_local("明天要處理慶修點餐的維護費 啊不對 是常青的維護費"),
      "明天要處理常青的維護費")
check("改口後面還有內容",
      D.correct_local("約 3 點 不對 4 點 然後記得帶合約"),
      "約 4 點 然後記得帶合約")
check("連續兩次改口（ASR 無標點）",
      D.correct_local("明天要處理慶修點餐的維護費 啊不對 是常青的維護費 然後 3 點 不對 4 點見"),
      "明天要處理常青的維護費 然後 4 點見")

print("\n[改口剖析] 絕不能被動到的（誤改比不改嚴重得多）")
for s in ["這樣做不對", "不對稱的設計比較好看", "你說對不對",
          "他不是故意的", "我是說真的", "改成這樣好嗎",
          "等等我一下", "這個答案不對嗎",
          # grok 負面陷阱表精選（2026-07-29）
          "系統今天不對勁 一直跳錯誤", "用了不對稱加密", "這題等等再說",
          "我是說如果客戶不續約呢", "可以打折 當我沒說", "數字對得起來"]:
    check(f"不動：{s}", D.correct_local(s), s)

print("\n[改口剖析] 沒把握就不動（寧可留標記給 LLM 層）")
src = "那個東西 不對 我想想"          # 無數字、無共同結尾 → 不動
check("無錨點不動", D.correct_local(src), src)

print("\n[熱鍵] 每個預設值都要解析得出來")
for name, combo in D.DEFAULT_CFG["hotkeys"].items():
    mods, vk = D.parse_hotkey(combo)
    check_true(f"{name} = {combo}", bool(vk), "parse 失敗")

print("\n[熱鍵] 不可以用 Alt+Space / Alt+Enter")
# 這兩個會讓底層組合鍵傳給 Windows：Alt+Space 跳系統選單搶焦點、
# Alt+Enter 在很多程式是全螢幕。實際踩過，症狀是「有時候貼得進去有時候不行」。
for name, combo in D.DEFAULT_CFG["hotkeys"].items():
    mods, vk = D.parse_hotkey(combo)
    bad = (mods & D.MOD_ALT) and vk in (0x20, 0x0D)
    check_true(f"{name} 沒踩 Alt+Space/Enter", not bad, combo)

print("\n[app 白話名稱]")
check("Word", D._app_label(r"C:\x\WINWORD.EXE", "WINWORD"), "📄 Word")
check("LINE", D._app_label(r"C:\x\LINE.exe", "LINE"), "💬 LINE")
check("Claude Code",
      D._app_label(r"C:\x\AppData\Roaming\Claude\claude-code\2.1\claude.exe", "claude"),
      "Claude Code")
check("未知的走 fallback", D._app_label(r"C:\x\weird.exe", "weird"), "weird")

print("\n[Protected-token guard] 小模型竄改要被擋（實測案例）")
check_true("英文被翻譯 → 擋", not D.guard_ok("我要做一個 skill", "我要做一個技能")[0])
check_true("數字形式改變 → 擋", not D.guard_ok("維護費 3000", "維護費 3,000")[0])
check_true("幻覺新增數字 → 擋", not D.guard_ok("約三點見", "約 3 點 15 分見")[0])
check_true("數字被刪 → 擋", not D.guard_ok("A 3000 B 5000", "A 3000 B")[0])
check_true("只加標點 → 過", D.guard_ok("維護費 3000", "維護費 3000。")[0])
check_true("大小寫差異 → 過（canonicalize 的事）",
           D.guard_ok("用 iphone 傳", "用 iPhone 傳")[0])
check_true("去口頭禪不動 token → 過",
           D.guard_ok("嗯 skill 做好了 3000 元", "skill 做好了，3000 元。")[0])

print("\n[背景模型升級] 硬體推薦與升級判斷")
check("GPU → medium", D._hw_recommend(gpu_ok=True, cores=4), ("medium", 5))
check("CPU 8 核 → small", D._hw_recommend(gpu_ok=False, cores=8), ("small", 5))
check("CPU 4 核 → base+beam1", D._hw_recommend(gpu_ok=False, cores=4), ("base", 1))
_orig_model, _orig_flag = D.CFG["model"], D.CFG.get("auto_upgrade_model", True)
D.CFG["auto_upgrade_model"] = False
check_true("關閉開關就不升級", D._upgrade_target() is None)
D.CFG["auto_upgrade_model"] = True
D.CFG["model"] = "large-v3"
check_true("已經 ≥ 推薦值就不升級", D._upgrade_target() is None)
D.CFG["model"], D.CFG["auto_upgrade_model"] = _orig_model, _orig_flag

print("\n[設定] 預設值健全性")
check_true("polish 有 providers", bool(D.DEFAULT_CFG["polish"].get("providers")))
check_true("tidy 預設開啟", D.DEFAULT_CFG["tidy"]["enabled"] is True)
m, b = D._first_run_model()
check_true("首次啟動模型在合法清單內", m in ("base", "small", "medium", "large-v3"), m)

print()
if fails:
    print(f"❌ {len(fails)} 項失敗：" + "、".join(fails))
    sys.exit(1)
print("✅ 全部通過")
