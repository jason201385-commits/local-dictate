# -*- coding: utf-8 -*-
"""拿外部生成的語料評測改口剖析器。
安全指標：負面案例（want==in）絕不能被動到——這是硬線。
正面案例沒改到只算保守（可接受），改錯才是問題。"""
import json, re, sys
sys.path.insert(0, r"C:\Claude 作品\local-dictate")
import dictate as D

raw = open(sys.argv[1], encoding="utf-8-sig").read()
# 剝 markdown fence 與雜訊行
lines = [l.strip() for l in raw.splitlines()
         if l.strip().startswith("{") and l.strip().endswith("}")]
cases = []
for l in lines:
    try:
        j = json.loads(l)
        if "in" in j and "want" in j:
            cases.append(j)
    except Exception:
        pass
print(f"可用案例 {len(cases)} 條\n")

viol, cons, exact, diff = [], [], 0, []
for c in cases:
    got = D.correct_local(c["in"])
    negative = c["in"].strip() == c["want"].strip()
    if negative:
        if got.strip() != c["in"].strip():
            viol.append((c, got))          # 🚨 安全違規
        else:
            exact += 1
    else:
        if got.strip() == c["want"].strip():
            exact += 1
        elif got.strip() == c["in"].strip():
            cons.append(c)                 # 保守沒動（可接受）
        else:
            diff.append((c, got))          # 改了但跟預期不同（要人工看）

print(f"完全符合預期   {exact}")
print(f"保守沒動（正例）{len(cons)}")
print(f"改了但不同     {len(diff)}")
print(f"🚨 安全違規     {len(viol)}")

if viol:
    print("\n=== 🚨 負面案例被誤改（必須修） ===")
    for c, got in viol:
        print(f"  in  : {c['in']}\n  got : {got}\n")
if diff:
    print("\n=== 改了但與預期不同（人工判讀） ===")
    for c, got in diff[:6]:
        print(f"  in  : {c['in']}\n  want: {c['want']}\n  got : {got}\n")
if cons:
    print("\n=== 保守沒動的正例（前 5，看有沒有該吃下的型態） ===")
    for c in cons[:5]:
        print(f"  in  : {c['in']}\n  want: {c['want']}\n")
