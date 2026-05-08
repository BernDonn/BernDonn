#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
from pathlib import Path
from typing import List, Tuple

SCREENSHOT_PATTERNS = [
    re.compile(r"^Screenshot.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^Screen Shot.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^Scherm.*\.(png|jpg|jpeg)$", re.IGNORECASE),
]

HELP_TEXT = """Totale /ss-overzicht nu:

• /ss
laatste screenshot nemen en uitleggen

• /ss huh
laatste screenshot extra duidelijk uitleggen

• /ss 3
van de laatste 3 screenshots één infographic maken

• /ss fix
screenshot analyseren en probleem helpen oplossen

• /ss do this
waarschijnlijke bedoeling uitvoeren op basis van de screenshot

• /ss note
laatste screenshot in een nieuwe Apple Note zetten

• /ss help
dit overzicht tonen"""

def is_screenshot_file(p: Path) -> bool:
    return p.is_file() and any(rx.match(p.name) for rx in SCREENSHOT_PATTERNS)

def newest_screenshots(base: Path, count: int) -> List[Path]:
    files = [p for p in base.iterdir() if is_screenshot_file(p)]
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files[:count]

def create_mac_note(paths: List[Path]) -> str:
    body = "\\n".join(["Imported screenshots:"] + [f"- {p.name}" for p in paths])
    script = f'''
    tell application "Notes"
      activate
      tell folder "Notes"
        make new note with properties {{name:"/ss note", body:"{body}"}}
      end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", script], check=False)
    return f"Apple Note aangemaakt met {len(paths)} screenshot(s)."

def parse_command(first: str | None, rest: List[str]) -> Tuple[int, str]:
    if first is None:
        return 1, "help"

    tokens = [first] + rest
    if tokens and tokens[0] == "/ss":
        tokens = tokens[1:]

    if not tokens:
        return 1, "huh"

    if tokens[0].lower() == "help":
        return 1, "help"

    if tokens[0].isdigit():
        count = max(1, int(tokens[0]))
        action = " ".join(tokens[1:]).strip()
        if not action:
            action = "make infographic" if count == 3 else "huh"
        return count, action

    return 1, " ".join(tokens).strip()

def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("first", nargs="?", default=None)
    parser.add_argument("rest", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    count, action = parse_command(args.first, args.rest)

    if action == "help":
        print(HELP_TEXT)
        return 0

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
    elif action.lower() == "note":
        if platform.system().lower() == "darwin":
            payload["result"] = create_mac_note(selected)
        else:
            payload["warning"] = "'note' werkt alleen op macOS."
    else:
        payload["result"] = "Forward selected files + action to ChatGPT for analysis/execution."

    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
