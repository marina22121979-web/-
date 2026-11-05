---
name: video-omni-restyle
description: DISABLED BY DEFAULT. Restyles one short clip into another visual style with Gemini Flash Image and Veo. Use ONLY when the user explicitly asks to restyle a specific clip; never propose it.
---
# omni-restyle

**Off unless the user asks.** The pipeline skips it, plans never propose it, and `generate.py restyle` refuses without
`--user-requested`. Use only when the user explicitly asks to restyle a named clip; record the request in `project.json`
(`"omni_restyle": {"requested": "<their words>", "clip": "..."}`). If a plan seems to need a different look, say so and
let the user decide.

**How it works:** Veo makes video from text and images (first frame, and last frame on newer models); it does not
repaint an existing clip frame by frame. So: restyle the clip's first (and optionally last) frame with Gemini Flash
Image, keeping composition, pose and framing; Veo animates from it (to the last frame with `--keep-end`), prompted with
the source's camera move and action. The look and staging carry over; **motion is regenerated**, so lips won't match
speech. Never restyle a talking shot whose audio stays; use it for B-roll, transitions, a memory beat, an illustrated
moment. If the user needs true frame-by-frame restyling of long footage, say this provider doesn't do it.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="videos/<project>"
```

1. Describe the clip's motion in one line from `watch.py focus` ("slow push-in, she turns toward the window").
2. **Gate 3**, without `--yes`:
   `python3 "$S/generate.py" restyle --clip "$W/broll/raw/x.mp4" --style-prompt "hand-drawn ink on cream paper, limited palette" --motion "<the line>" --keep-end --aspect 9:16 --seconds 8 --out "$W/broll/raw/x-ink.mp4" --price-per-second <p> --price-per-image <p> --user-requested`
3. Again with `--yes`: writes `x-ink-first-styled.png` (and `-last-styled.png`) and stops. Check them against the source
   frames (same composition, people, pose; nothing written).
4. Again with `--yes --confirm-stills`: Veo animates (OpenRouter only if it offers a video model; no guessed APIs).
5. `broll-conform.py --in "$W/broll/raw/x-ink.mp4" --out "$W/hyperframes/broll/x-ink.mp4" --start 0.3 --dur <slot>`, then a `clip` beat.

Style prompts name a medium and palette, not an artist ("flat vector illustration, two-tone charcoal and muted red";
"pencil sketch with light watercolour wash"), use the project's colours, and ask for identical composition. Everything
goes to `ledger.json` with `"ai_generated": true` and the `video-generate` disclosure rules. The user's own footage of
themselves is fine; other identifiable people or footage they don't own needs their rights first.
