#!/usr/bin/env python3
"""Ensure a fnOS FPK manifest file carries distributor=yunchui (our fork identity).

Usage:
    ensure-fnpak-distributor.py <path-to-manifest>

Safely updates distributor / distributor_url lines: replaces them if present,
appends after maintainer_url block if absent. Leaves every other line untouched.
"""

import re
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: ensure-fnpak-distributor.py <manifest>")
        return 2
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        txt = f.read()

    if re.search(r"^distributor\s*=", txt, re.M):
        txt = re.sub(
            r"^distributor\s*=.*$",
            "distributor           = yunchui",
            txt,
            flags=re.M,
        )
        txt = re.sub(
            r"^distributor_url\s*=.*$",
            "distributor_url       = https://github.com/yunchui/fnos_music_ext",
            txt,
            flags=re.M,
        )
    else:
        # 无 distributor 行：追加到 maintainer_url 之后
        block = (
            "\ndistributor           = yunchui\n"
            "distributor_url       = https://github.com/yunchui/fnos_music_ext"
        )
        if re.search(r"^maintainer_url\s*=", txt, re.M):
            txt = re.sub(
                r"(^maintainer_url\s*=.*$)",
                r"\1" + block,
                txt,
                count=1,
                flags=re.M,
            )
        else:
            txt = txt.rstrip("\n") + "\n" + block.lstrip("\n") + "\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
