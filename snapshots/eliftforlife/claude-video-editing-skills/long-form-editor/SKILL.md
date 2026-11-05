---
name: long-form-editor
description: Edit raw talking-head takes into a finished YouTube long form - transcribe, build a word-snapped cut list, grade and punch in on the A-roll, add word-synced motion graphics, generate original music and sound effects, mix and render one final file. Use when someone hands over raw takes and asks for an edit.
---

# Long-form editor

Everything is code, so every change is repeatable: a note like "music's too loud" becomes one number in one script.

## Folder layout
```
<video>/raw/          IMG_xxxx.MOV takes (+ screen recordings)
<video>/editor/       these scripts (copy from scripts/)
<video>/final/        output + upload text
```
Run everything from `editor/`. Needs ffmpeg, Python (`numpy scipy soundfile pillow faster-whisper`), Node + `playwright` (`npm i playwright && npx playwright install chromium`).

## Steps

1. **Check the footage first** with the `video-quality-check` skill (HDR? full range? dim?). Fix `TM`/`GR` in `build.py` to match.
2. **Transcribe.** Extract 16 kHz mono to `tr/IMG_x.wav` and 48 kHz stereo to `a48/IMG_x.wav`, then `py tr.py IMG_x ...` (Whisper with word timestamps).
3. **Find the story.** Read every transcript. Write `segs.py`: `(section, take, first-word start, START of last word[, hard out[, hard in]])`. Chapter slots are `('CARDn', None, seconds)`.
   - Hook first: the result, then the promise. Cut stammers and repeated phrases; prefer the clean re-say.
   - Re-transcribe a 5–10 s clip whenever a timing looks wrong. Whisper merges repeats and invents words in silence.
4. `py edl.py` → `plan.json`. Cuts snap to the quietest 10 ms near word edges, and pauses over 0.6 s shrink to 0.3 s.
5. `py words.py` → word times on the output timeline (`g/words.js`).
6. `py build.py` → graded, range-converted, punch-in A-roll (`aroll.mkv`). Set the face position per take in `FACE` so zooms stay centred.
7. `py voice.py` → `voice.wav` (crossfaded joins, EQ, de-ess, gentle compression, ~-14.5 LUFS).
8. **QA the cut:** re-transcribe `voice.wav` and read it start to finish. Fix `segs.py` and repeat 4–8 until it reads clean.
9. **Graphics:** write `g/_content.js` (see `example_content.js`), assemble `part2.js = _infra.js + _content.js + _tail.js`, then `node check.mjs`.
   - `block(section, 'start phrase', 'end phrase', html, {side})`. Children with `data-at="phrase"` reveal on that word.
   - One graphic at a time, opposite side from the face, never over it. Render sample frames and look at them before the full render.
10. `py music.py` → original score + sound effects timed to the sections and graphics (no licensed music needed). Then `py mix.py` → music ~20 dB under the voice, oversampled true-peak limiter.
11. **Render graphics:** in `g/`, run `node render.mjs <from> <to>` in 3–4 parallel chunks.
12. `py final.py` → one composite pass, CRF 14 slow, AAC 320k.

## Taste rules
- One focal point on screen. No subtitles top and bottom at the same time.
- Graphics say less than the voice: 2–4 words big, one small line under.
- Never put a number on screen that wasn't said or verified.
- Chapter cards between steps; a short end card.
