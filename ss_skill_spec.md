# /ss skill prompt (clarified)

Use this skill when the user starts a message with `/ss`.

## Goal
Make screenshot-based collaboration fast: fetch the newest screenshots, then execute the user’s requested action on them.

## Command format
`/ss [count] [action text...]`

- `count` is optional and must be a positive integer.
- If `count` is missing, default to `1`.
- If `action text` is missing, ask a brief follow-up question.

## Source folder
Use the Desktop as the screenshot source folder.

- macOS: `~/Desktop`
- Linux: `~/Desktop`
- Windows: `%USERPROFILE%/Desktop`

## Selection rules
1. List files in the screenshot folder sorted **newest → oldest** by modified time.
2. Select the first `count` files from that list.
3. If fewer files exist than requested, use all available and tell the user.

## Action routing
After selecting screenshots, treat the remaining text as the requested action.

Examples:
- `/ss huh` → analyze the latest screenshot and explain what it shows.
- `/ss 3 make infographic plz` → use the 3 newest screenshots to create one unified infographic.
- `/ss fix` → inspect screenshot(s) for errors (code or UI), diagnose likely root cause, and propose or apply a fix.
- `/ss do this` → infer the pattern shown in screenshot(s), then produce a goal-oriented remix tailored to the user.
- `/ss note` → place the newest selected screenshot into a new note in Apple Notes on Mac, with a short title and timestamp.

## Behavior and safety notes
- Never ignore the action text; parsing priority is: `/ss` → optional count → action.
- If parsing is ambiguous, ask one concise clarifying question.
- Keep output structured: (1) selected files, (2) interpretation, (3) action result.
- For code/UI fixes, include concrete next steps and optionally patch suggestions.
- If the action is `note`, create a new Mac note and attach the selected screenshot(s); include the original filename(s) in the note body.
