#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import platform
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

SCREENSHOT_PATTERNS = [
    re.compile(r"^Screenshot.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^Screen Shot.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^Scherm.*\.(png|jpg|jpeg)$", re.IGNORECASE),
    re.compile(r"^SS .*?\.(png|jpg|jpeg)$", re.IGNORECASE),
]

HELP_TEXT = """ss commands:
  /ss          explain latest screenshot clearly
  /ss huh      explain what is happening
  /ss 3        make infographic intent from newest 3
  /ss fix      diagnose likely issue and next fix
  /ss do this  infer requested action from screenshot
  /ss note     create Apple Note with text + screenshot(s)
  /ss help     show this overview"""


@dataclass(frozen=True)
class Command:
    count: int
    intent: str
    raw: str


def is_screenshot_file(path: Path) -> bool:
    return path.is_file() and any(pattern.match(path.name) for pattern in SCREENSHOT_PATTERNS)


def newest_screenshots(base: Path, count: int) -> list[Path]:
    screenshots = [path for path in base.iterdir() if is_screenshot_file(path)]
    screenshots.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return screenshots[:count]


def parse_command(argv: Sequence[str]) -> Command:
    tokens = list(argv)
    if tokens and tokens[0] == "/ss":
        tokens = tokens[1:]

    if not tokens:
        return Command(count=1, intent="huh", raw="/ss")

    if tokens[0].lower() == "help":
        return Command(count=1, intent="help", raw=" ".join(tokens))

    count = 1
    if tokens[0].isdigit():
        count = max(1, int(tokens.pop(0)))

    intent = " ".join(tokens).strip()
    if not intent:
        intent = "make infographic" if count == 3 else "huh"

    return Command(count=count, intent=intent, raw=" ".join(argv).strip())


def format_selected(paths: Sequence[Path]) -> str:
    if not paths:
        return "Selected: none"

    lines = ["Selected newest -> oldest:"]
    for index, path in enumerate(paths, start=1):
        modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"{index}. {path.name} ({modified})")
    return "\n".join(lines)


def analysis_prompt(command: Command, paths: Sequence[Path]) -> str:
    file_lines = "\n".join(f"- {path}" for path in paths) if paths else "- No screenshots found"
    return f"""Analysis prompt:
Use the selected screenshot(s) to answer the user's /ss command directly in chat.

Intent: {command.intent}
Files:
{file_lines}

Return compactly:
1. What is visible or likely happening.
2. The best next action/result for intent "{command.intent}".
3. Any concrete fix, note text, or infographic structure needed."""


def interpret(command: Command) -> str:
    intent = command.intent.lower()
    if intent == "huh":
        return "Interpretation: explain the newest screenshot in plain language."
    if intent == "make infographic":
        return "Interpretation: make one infographic concept from the selected screenshots."
    if intent == "fix":
        return "Interpretation: diagnose the visible issue and propose the most direct fix."
    if intent == "do this":
        return "Interpretation: infer the intended action from the screenshot and perform it in chat."
    if intent == "note":
        return "Interpretation: create an Apple Note with short text and selected screenshot(s)."
    return f"Interpretation: {command.intent}"


def apple_script_quote(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def create_mac_note(paths: Sequence[Path], command: Command) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    title = f"/ss note {timestamp}"
    file_list = "<br>".join(f"- {path.name}" for path in paths)
    body = (
        f"<h1>{title}</h1>"
        f"<p>Command: {command.raw or '/ss note'}</p>"
        f"<p>Selected newest to oldest:</p><p>{file_list}</p>"
    )

    script_lines = [
        'tell application "Notes"',
        "activate",
        f'set newNote to make new note at folder "Notes" with properties {{name:"{apple_script_quote(title)}", body:"{apple_script_quote(body)}"}}',
    ]
    for path in paths:
        script_lines.append(f'set imageFile to POSIX file "{apple_script_quote(str(path))}"')
        script_lines.append("make new attachment at end of newNote with data imageFile")
    script_lines.append("end tell")

    result = subprocess.run(
        ["osascript", "-e", "\n".join(script_lines)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown osascript error"
        return f"Note failed: {detail}"
    return f"Apple Note created: {title} ({len(paths)} screenshot(s))."


def maybe_ai_available() -> bool:
    return bool(os.environ.get("OPENAI_API_KEY"))


def run(command: Command, desktop: Path) -> int:
    if command.intent == "help":
        print(HELP_TEXT)
        return 0

    if not desktop.exists():
        print(f"Desktop not found: {desktop}")
        return 1

    selected = newest_screenshots(desktop, command.count)

    print(format_selected(selected))
    print(interpret(command))

    if len(selected) < command.count:
        print(f"Notice: requested {command.count}, found {len(selected)}.")

    if command.intent.lower() == "note":
        if not selected:
            print("Result: no screenshots found, no note created.")
            return 1
        if platform.system().lower() != "darwin":
            print("Result: /ss note works only on macOS.")
            return 1
        print(f"Result: {create_mac_note(selected, command)}")
        return 0

    if maybe_ai_available():
        print("Result: AI key detected, but Route A leaves final interpretation to the chat orchestrator.")
    else:
        print("Result: no OPENAI_API_KEY required; use this fallback in chat.")
    print(analysis_prompt(command, selected))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ss",
        description="Local /ss screenshot selector for chat-orchestrator sessions.",
    )
    parser.add_argument("args", nargs=argparse.REMAINDER)
    parser.add_argument("--desktop", type=Path, default=Path.home() / "Desktop")
    parsed = parser.parse_args()

    command = parse_command(parsed.args)
    return run(command, parsed.desktop)


if __name__ == "__main__":
    raise SystemExit(main())
