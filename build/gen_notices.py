#!/usr/bin/env python3
"""從實際安裝環境產生第三方元件清單,並收割授權原文到 licenses/。

**為什麼需要這支腳本**(2026-07-30 實測踩到,不是預防性設計):
手工維護 THIRD_PARTY_NOTICES.md 出了兩種錯,而且兩種都不會有任何徵兆——

  1. 漏元件:v0.1.3 出貨的 portable.zip 裡有 `click 8.4.2`,清單裡沒有。
     click 是被相依進來的,沒人「決定」要加它,所以也沒人想到要列它。
  2. 版本錯:清單寫 tqdm 4.67.3(從開發機收割),CI 乾淨環境實際裝的是 4.70.0。
     requirements.txt 沒有 pin 版本,所以每次 build 的版本都可能不一樣。

結論:**清單必須從「這一次 build 真正裝了什麼」產生,不能靠人記得。**

用法:
    python build/gen_notices.py --write     # 更新 THIRD_PARTY_NOTICES.md 的自動產生區塊 + 收割 licenses/
    python build/gen_notices.py --check     # 只檢查有沒有漏,有漏就 exit 1(給 CI 當閘門用)

自動產生的只有「Python 套件」那張表(標記區塊之間)。原生函式庫、模型、執行環境那幾張表
是人工判斷的結果(例如 FFmpeg 是不是 LGPL 組態),腳本不碰。
"""
from __future__ import annotations

import argparse
import importlib.metadata as md
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTICES = os.path.join(ROOT, "THIRD_PARTY_NOTICES.md")
LICENSES_DIR = os.path.join(ROOT, "licenses")

BEGIN = "<!-- BEGIN AUTOGEN:PYTHON-PACKAGES -->"
END = "<!-- END AUTOGEN:PYTHON-PACKAGES -->"

# 只在建置階段用到、不會進到產物裡的東西 —— 列進清單反而誤導使用者。
BUILD_ONLY = {
    "pyinstaller", "pyinstaller-hooks-contrib", "altgraph", "pefile",
    "pywin32-ctypes", "setuptools", "wheel", "pip", "packaging",
}

# 這幾份是人工從 gnu.org 取得的規範文本,不屬於任何 wheel,清理孤兒時要留著。
# LGPL-3.0 是 GPL-3.0 的補充條款,依 LGPL-3.0 要求必須一併提供 GPL-3.0 全文。
KEEP_ALWAYS = ("LGPL-2.1.txt", "LGPL-3.0.txt", "GPL-3.0.txt")

# 這幾個上游 wheel 沒有把授權檔放進 dist-info,只能給連結。
UPSTREAM_LICENSE_URL = {
    "ctranslate2": "https://github.com/OpenNMT/CTranslate2/blob/master/LICENSE",
    "tokenizers": "https://github.com/huggingface/tokenizers/blob/main/LICENSE",
    "tqdm": "https://github.com/tqdm/tqdm/blob/master/LICENCE",
    "click": "https://github.com/pallets/click/blob/main/LICENSE.txt",
}


def norm(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def license_of(dist: md.Distribution) -> str:
    """先看 License-Expression(PEP 639),再看 classifier,最後才看自由文字 License 欄。"""
    meta = dist.metadata
    expr = meta.get("License-Expression")
    if expr:
        return expr.strip()
    cls = [c.split("::")[-1].strip() for c in (meta.get_all("Classifier") or []) if c.startswith("License ::")]
    if cls:
        return "; ".join(dict.fromkeys(cls))
    lic = (meta.get("License") or "").strip()
    if lic and "\n" not in lic and len(lic) <= 60:
        return lic
    return "見授權原文"


def harvest(dist: md.Distribution) -> str | None:
    """把 wheel dist-info 裡的授權檔複製到 licenses/,回傳檔名。"""
    for f in dist.files or []:
        base = os.path.basename(str(f)).lower()
        if not base.startswith(("license", "copying", "notice")):
            continue
        src = dist.locate_file(f)
        if not os.path.isfile(src):
            continue
        out = f"{dist.metadata['Name']}-{dist.version}-{os.path.basename(str(f))}"
        os.makedirs(LICENSES_DIR, exist_ok=True)
        shutil.copy(src, os.path.join(LICENSES_DIR, out))
        return out
    return None


def roots_from_requirements() -> list[str]:
    """讀 requirements.txt 的頂層套件名(nvidia-* 除外——CI 刻意不打包 CUDA)。"""
    path = os.path.join(ROOT, "requirements.txt")
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line:
            continue
        name = re.split(r"[<>=!~\[;]", line)[0].strip()
        if name and not norm(name).startswith("nvidia-"):
            out.append(name)
    return out


def runtime_deps(dist: md.Distribution) -> list[str]:
    """該套件的執行期相依。

    排除兩種不會進到 Windows 產物的東西,否則清單會出現一堆「找不到」的假警報:
      · extras —— 沒裝 extra 就不會被打包
      · 別的平台 —— 例如 pynput 在 Linux 要 evdev/python-xlib、macOS 要 pyobjc
    """
    deps = []
    for req in dist.requires or []:
        req = req.strip()
        if "extra ==" in req:
            continue
        if ";" in req:
            marker = req.split(";", 1)[1]
            try:
                from packaging.markers import Marker
                if not Marker(marker).evaluate():
                    continue
            except ImportError:
                # 沒有 packaging 就退回字串判斷:明確指名別的平台就跳過
                low = marker.lower()
                if any(p in low for p in ("linux", "darwin", "macos", "aix", "freebsd")):
                    continue
            except Exception:
                pass  # marker 解析不了就保守納入,寧可多列不要漏
        name = re.split(r"[<>=!~\[;( ]", req)[0].strip()
        if name:
            deps.append(name)
    return deps


def collect() -> list[dict]:
    """從 requirements.txt 出發做 BFS,得到真正會被打包的相依閉包。

    不直接列「環境裡所有套件」——開發機通常還裝了別的專案的東西,
    那樣產生的清單在本機和 CI 會不一樣,反而失去可信度。
    """
    queue = list(roots_from_requirements())
    seen_names: set[str] = set()
    rows = []
    missing: list[str] = []

    while queue:
        name = queue.pop(0)
        if norm(name) in seen_names or norm(name) in {norm(b) for b in BUILD_ONLY}:
            continue
        seen_names.add(norm(name))
        if norm(name).startswith("nvidia-"):
            continue
        try:
            dist = md.distribution(name)
        except md.PackageNotFoundError:
            missing.append(name)
            continue
        rows.append({
            "name": dist.metadata["Name"] or name,
            "version": dist.version,
            "license": license_of(dist),
            "file": harvest(dist),
        })
        queue.extend(runtime_deps(dist))

    if missing:
        print(f"  ⚠️ 這些相依在目前環境找不到,清單會漏:{', '.join(sorted(set(missing)))}",
              file=sys.stderr)
    # 去重(同名不同大小寫)後排序
    seen, out = set(), []
    for r in sorted(rows, key=lambda r: norm(r["name"])):
        if norm(r["name"]) in seen:
            continue
        seen.add(norm(r["name"]))
        out.append(r)
    return out


def render(rows: list[dict]) -> str:
    lines = [
        BEGIN,
        "",
        f"<!-- 這張表由 build/gen_notices.py 從實際安裝環境產生,共 {len(rows)} 個套件。不要手改。 -->",
        "",
        "| 元件 | 版本 | 授權 | 原文 |",
        "|---|---|---|---|",
    ]
    for r in rows:
        if r["file"]:
            ref = f"`licenses/{r['file']}`"
        else:
            url = UPSTREAM_LICENSE_URL.get(norm(r["name"]).replace("-", ""))
            url = url or UPSTREAM_LICENSE_URL.get(norm(r["name"]))
            ref = f"[上游 LICENSE]({url})(wheel 未附檔)" if url else "wheel 未附檔,見上游 repo"
        lines += [f"| {r['name']} | {r['version']} | {r['license']} | {ref} |"]
    lines += ["", END]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true", help="更新 THIRD_PARTY_NOTICES.md 並收割 licenses/")
    g.add_argument("--check", action="store_true", help="只檢查,不一致就 exit 1")
    args = ap.parse_args()

    rows = collect()
    block = render(rows)

    if not os.path.exists(NOTICES):
        print(f"!! 找不到 {NOTICES}", file=sys.stderr)
        return 2
    text = open(NOTICES, encoding="utf-8").read()

    if BEGIN not in text or END not in text:
        print(f"!! {os.path.basename(NOTICES)} 缺少 {BEGIN} / {END} 標記區塊", file=sys.stderr)
        return 2

    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)

    if args.check:
        if new != text:
            print("!! THIRD_PARTY_NOTICES.md 與實際安裝環境不一致。")
            print("   跑 `python build/gen_notices.py --write` 更新後重新提交。")
            old_names = set(re.findall(r"^\| ([A-Za-z0-9_.\-]+) \|", text, re.M))
            new_names = {r["name"] for r in rows}
            missing = sorted(n for n in new_names if n not in old_names)
            if missing:
                print(f"   清單漏掉的元件:{', '.join(missing)}")
            return 1
        print(f"OK:{len(rows)} 個套件,清單與環境一致。")
        return 0

    open(NOTICES, "w", encoding="utf-8", newline="\n").write(new)
    harvested = sum(1 for r in rows if r["file"])
    print(f"已更新 {os.path.basename(NOTICES)}:{len(rows)} 個套件,收割 {harvested} 份授權原文到 licenses/")
    for r in rows:
        if not r["file"]:
            print(f"  ⚠️ {r['name']} {r['version']} 的 wheel 沒附授權檔,用上游連結")

    # 清掉不再被引用的授權檔(套件升版或改名會留下孤兒)。
    # 保護:只有在這次收割量看起來正常時才清,免得環境不完整就把東西刪光。
    if harvested >= 20:
        keep = {r["file"] for r in rows if r["file"]} | set(KEEP_ALWAYS)
        for name in sorted(os.listdir(LICENSES_DIR)):
            if os.path.isfile(os.path.join(LICENSES_DIR, name)) and name not in keep:
                os.remove(os.path.join(LICENSES_DIR, name))
                print(f"  🗑 移除孤兒授權檔:{name}")
    else:
        print(f"  ⚠️ 只收割到 {harvested} 份,略過孤兒清理(環境可能不完整)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
