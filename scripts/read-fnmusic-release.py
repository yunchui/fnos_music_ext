#!/usr/bin/env python3
"""Read the latest fnmusic-ext release and print version/sha256/size/url as JSON.

Usage:
    read-fnmusic-release.py               # latest release
    read-fnmusic-release.py <version>     # a specific tag version (e.g. 2.2.3)

Env:
    GH_TOKEN: PAT with read access to yunchui/fnos_music_ext releases.

Exits non-zero if no fnmusic-ext-*.fpk asset found or digest missing/invalid.
"""

import json
import os
import sys
import urllib.request


def api(url):
    token = os.environ.get("GH_TOKEN", "")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "fnmusic-sync",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def pick(rel):
    for a in rel.get("assets", []):
        if a["name"].startswith("fnmusic-ext-") and a["name"].endswith(".fpk"):
            return a
    return None


def main() -> int:
    base = "https://api.github.com/repos/yunchui/fnos_music_ext"
    if len(sys.argv) >= 2:
        ver = sys.argv[1].lstrip("v")
        rel = api(f"{base}/releases/tags/v{ver}")
        if not rel or "tag_name" not in rel:
            print(f"ERROR: release v{ver} 不存在", file=sys.stderr)
            return 1
    else:
        rel = api(f"{base}/releases/latest")
    asset = pick(rel)
    if not asset:
        print("ERROR: release 无 fnmusic-ext-*.fpk 资产", file=sys.stderr)
        return 1
    digest = asset.get("digest", "").replace("sha256:", "").rstrip()
    if not digest or len(digest) != 64:
        print("ERROR: sha256 无效或缺失，拒绝写入坏校验值", file=sys.stderr)
        return 1
    info = {
        "version": rel["tag_name"].lstrip("v"),
        "url": asset["browser_download_url"],
        "sha256": digest,
        "size": asset["size"],
        "published": rel.get("published_at") or "",
    }
    with open("/tmp/fnmusic_release.json", "w", encoding="utf-8") as f:
        json.dump(info, f)
    print("detected:", json.dumps(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
