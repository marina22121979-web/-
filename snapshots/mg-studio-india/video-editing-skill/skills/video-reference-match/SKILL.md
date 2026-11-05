---
name: video-reference-match
description: Matches a project's footage, a user-supplied reference video/image, or a written concept against the built-in library of 50 measured, brand-neutral style blueprints, asks the user whether to use a match (Gate R, every project), and turns the chosen blueprint into an editing roadmap - structure, pacing, captions, background text, motion graphics, cut-outs/silhouettes, layout, camera, transitions, sound and catalog style IDs - plus a brand prompt. Use at every project start, and when the user says "make it look like this", "use a reference", "what style fits", or gives no reference at all.
---

# Reference match (style blueprints, Gate R)

> [!IMPORTANT]
> **References Precedence Contract**: User-provided references (videos, screenshots, or benchmark files in `references/`, `videos/<project>/references/`, or passed via prompt/CLI) **ALWAYS take absolute precedence over blueprints**. The 50 blueprints provide proven baseline systems, but when a reference is supplied, its measured structure, layout choices (e.g. split-screen with speaker in bottom pane), pacing, and visual devices override the blueprint defaults.

A library of **50 style blueprints**, each a measured editing system with no source identity: what makes it distinct,
structure by % of runtime, pacing, caption spec (sizes solved for local fonts, colours as brand roles, frame timings),
background text, motion graphics, cut-outs, layout, camera, transitions, sound, the catalog styles it uses,
linked verified HyperFrames compositions (`hyperframes_compositions`), when to use
and avoid it, and a brand prompt. Grade is never copied: it is built from the project's own footage; a blueprint only
gives a look intent. In split-screen video, the speaker takes the bottom (70% of the time), with top and bottom cropped
to keep the focus on head area visibility.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"   # shared engine (watch, transcribe, render)
RM="${VIDEO_SKILLS:-$HOME/.agents/skills}/video-reference-match"
PY="$PROJECT/.venv/bin/python3"; W="videos/<project>"
```

| File | What |
|---|---|
| `references/index.json` | one row per blueprint (what the matcher reads) |
| `references/blueprints/Bxx.json` | the full blueprint ([schema](references/blueprint-schema.md)) |
| `references/INDEX.md` | blueprints grouped by caption family, signatures, tags |
| `references/PROMPTS.md` | every blueprint's brand prompt |
| `references/weights.json` | matching columns and weights, similarity threshold |
| `scripts/match.py` | rank blueprints for a video / image / concept; `--pick` writes `ROADMAP.md` |
| `scripts/caption_probe.py`, `scripts/fit_font.py` | VERIFY: measure rendered text; expected ink for any word at a px size |
| `scripts/build_index.py`, `scripts/check_blueprints.py` | rebuild the index after editing a blueprint; schema + anonymity check |
| `scripts/measure_blueprint.py` | the `measured` block for a new blueprint (from a video + its `watch.py ref` output) |

## Gate R: on every project start (after transcription, before format selection)

1. **Collect the inputs.** References the user gave (videos, images, a written concept) and, always, the project's
   own raw take + transcript.
2. **Match.**
   ```bash
   "$PY" "$RM/scripts/match.py" --video "$W/raw/<clip>" --transcript "$W/transcript-raw.json" \
       [--video <reference.mp4>] [--image <ref.png>] [--concept "<what the user described>"] [--tags a,b] \
       --out "$W/reference-match"
   ```
   Scores are weighted per column (`weights.json`: format, concept text, footage needs, pacing, people on screen,
   language, aspect, duration, tags; grade and music weigh 0). Only columns the input can show are used.
3. **Ask, every time.**
   - **Similar blueprints found** (`similar_found: true`): show the top 2-3 (ID, score, one-line signature, the
     distinctive devices, what footage it needs) and ask: *"These styles in the reference index match your video. Use
     one to style it? (use B07 / mix B07 captions + B21 cards / no, keep my own direction)"*.
   - **User gave no reference** (whatever the scores): show the 3 closest blueprints **and** 3-4 matching styles from
     `video-plan-storyboard/references/style-catalog.md`, and ask the user to pick one, mix two, or describe their own.
   - **References given but nothing similar**: say so, and continue with the user's references through
     `video-watch ref` and the catalog; offer the closest blueprint as an option only.
   Never apply a blueprint without the answer. Record it in `project.json` → `gates.reference`
   (`{"answer": "B07" | "mix" | "none", "at": ..., "matches": [...]}`).
4. **Roadmap.** For the chosen blueprint(s):
   `"$PY" "$RM/scripts/match.py" ... --pick B07[,B21] --out "$W/reference-match"` → `ROADMAP.md`: structure mapped to
   the project's runtime, pacing targets, and per element (captions, background text, motion graphics, cards, cut-outs,
   B-roll, layout, camera, transitions, end card, sound) what / how / when with catalog style IDs, and linked HyperFrames
   compositions to mount (`compositions/`); the grade line points
   to the project's own footage. `video-plan-storyboard` builds `plan.md` from it (cite `#ID Name` for every style) and
   `video-style` fills the brand tokens.
5. **Brand prompt.** The blueprint's `brand_prompt` is the caption/text spec against brand tokens (`{{ACCENT}}`,
   `{{FONT_DISPLAY}}`, ...). Fill the tokens from the brand (or `style.json`), never from the blueprint's defaults unless
   the user has no brand; keep the geometry, sizes and timings exact. Run its VERIFY step after the first caption
   render (`caption_probe.py`; expected ink for any word via `fit_font.py`).

## Using a match well

- Take what makes the blueprint distinct (`signature.unique_devices`) first; generic parts (plain captions, hard cuts)
  are not why it was chosen.
- A blueprint's `match.needs` must fit the footage: no speaker footage → no speaker-led blueprint; no screen
  recordings → drop screen-insert devices or generate them (`video-generate`, with cost approval).
- Mixing: captions from one blueprint + cards/background text from another is fine; keep one accent colour and two
  font families at most.
- Pacing targets come from the blueprint; the cut still keeps every word of the approved story (`video-cut-audit`).

## Maintaining the library

Edit `references/blueprints/Bxx.json` directly, then `scripts/build_index.py` and `scripts/check_blueprints.py`
(must print 0 problems). Blueprints never name a creator, brand, person, place, file or quote, and never carry
frames; add a new blueprint by writing the same schema with the next free ID.
