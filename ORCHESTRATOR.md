# /ss Codex orchestrator

Exact Route A usage in Codex sessions:

1. User types `/ss ...`.
2. Run local helper:

   ```sh
   ss ...
   ```

3. Use the newest -> oldest selected screenshots from `~/Desktop`.
4. Interpret the command:
   - `/ss` and `/ss huh`: explain what is visible.
   - `/ss 3`: create a compact infographic structure.
   - `/ss fix`: diagnose and give the fix.
   - `/ss do this`: infer the intended action and produce it.
   - `/ss note`: create Apple Note via the helper.
   - `/ss help`: show the command overview.
5. If no AI call is available, paste/use the helper's `Analysis prompt` and
   answer directly in chat. `OPENAI_API_KEY` is optional, never required.

