# -*- coding: utf-8 -*-
"""建立兩個捷徑：

1. 開始功能表捷徑 + **全域快速鍵**（預設 Ctrl+Alt+V）→ 不小心關掉時一鍵叫回來
2. 開機自動啟動（選配）

用法：
    python setup_shortcuts.py                  # 建立快速鍵捷徑
    python setup_shortcuts.py CTRL+ALT+J       # 換一組快速鍵
    python setup_shortcuts.py --startup        # 順便設定開機自動啟動
    python setup_shortcuts.py --remove         # 全部移除

原理：Windows 的 .lnk 檔有一個「快速鍵」屬性，只要捷徑放在「開始功能表」或
「桌面」，這組鍵就是全域生效的——不用裝 AutoHotkey，也不用多跑一個常駐程式。
"""
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "dictate.py"
NAME = "local-dictate 口述引擎"

args = [a for a in sys.argv[1:]]
REMOVE = "--remove" in args
STARTUP = "--startup" in args
hotkeys = [a for a in args if not a.startswith("--")]
HOTKEY = (hotkeys[0] if hotkeys else "CTRL+ALT+V").upper()


def pythonw():
    """用 pythonw 而不是 python，這樣啟動不會閃一個黑視窗。"""
    p = Path(sys.executable)
    cand = p.with_name("pythonw.exe")
    return str(cand if cand.exists() else p)


def run_ps(script):
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-Command", "-"],
                       input=script, text=True, capture_output=True)
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        print("PowerShell 失敗：", (r.stderr or "").strip()[:300])
    return r.returncode == 0


start_menu = Path(os.environ["APPDATA"]) / "Microsoft/Windows/Start Menu/Programs"
startup = start_menu / "Startup"
lnk_hotkey = start_menu / f"{NAME}.lnk"
lnk_startup = startup / f"{NAME}.lnk"

if not SCRIPT.exists():
    sys.exit(f"❌ 找不到 {SCRIPT}")

if REMOVE:
    for f in (lnk_hotkey, lnk_startup):
        if f.exists():
            f.unlink()
            print(f"已移除 {f.name}（{f.parent}）")
        else:
            print(f"（沒有 {f.name}，跳過）")
    sys.exit(0)

PS = r"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{lnk}')
$s.TargetPath = '{exe}'
$s.Arguments = '"{script}"'
$s.WorkingDirectory = '{cwd}'
$s.Description = '本機繁中語音輸入'
$s.WindowStyle = 7
{extra}
$s.Save()
Write-Output '建立 {lnk}'
"""

ok = run_ps(PS.format(lnk=lnk_hotkey, exe=pythonw(), script=SCRIPT, cwd=HERE,
                      extra=f"$s.Hotkey = '{HOTKEY}'"))
if ok:
    print(f"✅ 快速鍵 {HOTKEY} 已設定 — 任何時候按它就會啟動口述引擎")
    print("   （已經在跑的話會跳出提示，不會開出第二個實例）")
    print(f"   要換一組：到「{lnk_hotkey}」按右鍵 → 內容 → 快速鍵，或重跑本程式帶新的鍵")

if STARTUP:
    if run_ps(PS.format(lnk=lnk_startup, exe=pythonw(), script=SCRIPT, cwd=HERE,
                        extra="")):
        print("✅ 開機自動啟動已設定")

print("\n移除：python setup_shortcuts.py --remove")
