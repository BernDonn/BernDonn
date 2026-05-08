# ss tool

Local helper for Route A: a Codex/chat-orchestrator flow for `/ss` commands.

The tool never requires `OPENAI_API_KEY`. It selects the newest screenshots from
`~/Desktop`, prints a compact interpretation, and returns a structured analysis
prompt that the agent can answer directly in chat when no AI call is available.

## Commands

```sh
ss help
ss huh
ss 3
ss fix
ss do this
ss note
```

Equivalent slash form is also accepted:

```sh
ss /ss 3
```

## Behavior

- Selection is newest -> oldest by file modified time.
- `/ss` defaults to `huh`.
- `/ss 3` defaults to `make infographic`.
- `/ss note` creates an Apple Note with a short text body and the selected
  screenshot attachment(s).
- Non-note commands print an `Analysis prompt` fallback for the chat
  orchestrator. This is the expected local path when no `OPENAI_API_KEY` exists.

## Screenshot names

Recognized screenshot files on the Desktop:

- `Screenshot*.png|jpg|jpeg`
- `Screen Shot*.png|jpg|jpeg`
- `Scherm*.png|jpg|jpeg`
- `SS *.png|jpg|jpeg`

## Codex usage

When the user types `/ss ...` in a Codex session:

1. Run `ss ...` locally from this repo, or add this directory to `PATH`.
2. Read the selected file list and analysis prompt.
3. Inspect the screenshot(s) if needed.
4. Answer directly in chat with a compact useful result.

