#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, platform, re
from pathlib import Path

SCREENSHOT_PATTERNS = [
    re.compile(r"^Screenshot.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^Screen Shot.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^Scherm.*\.(png|jpg|jpeg)$", re.IGNORECASE),
]

def is_screenshot_file(p: Path) -> bool:
    return p.is_file() and any(rx.match(p.name) for rx in SCREENSHOT_PATTERNS)

def newest_screenshots(base: Path, count: int):
    files = [p for p in base.iterdir() if is_screenshot_file(p)]
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files[:count]

def main() -> int:
    parser = argparse.ArgumentParser(description="/ss helper")
    parser.add_argument("first", nargs="?", default=None)
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    if args.first is None:
        print("Use: ss [count] [action]")
        return 1

    if args.first.isdigit():
        count = max(1, int(args.first))
        action = " ".join(args.rest).strip()
    else:
        count = 1
        action = " ".join([args.first] + args.rest).strip()

    if not action:
        print("No action given. Example: ss 3 fix")
        return 1

    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        print(f"Desktop not found: {desktop}")
        return 1

    selected = newest_screenshots(desktop, count)
    payload = {
        "selected_files": [str(p) for p in selected],
        "count_requested": count,
        "count_selected": len(selected),
        "action": action,
    }

    if not selected:
        payload["warning"] = "No screenshot files found on Desktop."
    elif action.lower() == "note" and platform.system().lower() == "darwin":
        payload["result"] = "Create Apple Note step can be added next; files are selected correctly."
    else:
        payload["result"] = "Forward selected files + action to ChatGPT for analysis/execution."

    print(json.dumps(payload, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
