#!/usr/bin/env python3
"""Update the fnmusic-ext entry in a fnpack.json from a release-info JSON file.

Usage:
    update-fnpack-fnmusic-ext.py <fnpack.json> <release-info.json>

release-info.json shape (produced by read-fnmusic-release.py):
    {"version": "2.2.3", "url": "...", "sha256": "...", "size": 123, "published": "..."}
"""

import json
import sys
from datetime import datetime, timedelta, timezone


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: update-fnpack-fnmusic-ext.py <fnpack.json> <release-info.json>")
        return 2
    fnp, relfile = sys.argv[1], sys.argv[2]
    info = json.load(open(relfile, encoding="utf-8"))
    ver = info["version"]

    with open(fnp, encoding="utf-8") as f:
        d = json.load(f)
    entry = (d.get("apps") or {}).get("fnmusic-ext")
    if not entry:
        print("fnos-source 无 fnmusic-ext 条目，跳过")
        return 0

    published = info.get("published", "").replace("Z", "+00:00")
    if published:
        dt = datetime.fromisoformat(published).astimezone(
            timezone(timedelta(hours=8)))
        updated = dt.strftime("%Y-%m-%dT%H:%M:%S+08:00")
    else:
        updated = datetime.now(timezone(timedelta(hours=8))).strftime(
            "%Y-%m-%dT%H:%M:%S+08:00")

    prev_release = entry.get("releases", {}).get(ver, {})
    new_rel = {
        "changelog": "跟随上游 javycoder/fnos_music_ext 自动同步。",
        "updated_at": updated,
        "os_min_version": prev_release.get("os_min_version", "1.2.0"),
        "packages": {
            "all": {
                "download_url": info["url"],
                "sha256": info["sha256"],
                "size": info["size"],
            }
        },
    }
    releases = entry.setdefault("releases", {})
    if ver not in releases or releases.get(ver) != new_rel:
        releases[ver] = new_rel
        with open(fnp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print("fnpack.json 已更新 fnmusic-ext ->", ver)
    else:
        print("fnmusic-ext 已是 %s，无变更" % ver)
    return 0


if __name__ == "__main__":
    sys.exit(main())
