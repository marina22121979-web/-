---
name: video-scripted-narration
description: Produce a long-form narrated video from a verbatim script. The presenter reads the script per segment; ASR + character-level alignment map the known text onto the recording, and cue phrases in the script fire slides/cards at the right moment in an editable FCP7 XML timeline. Use when exact wording matters (compliance, tight runtime, translated narration) AND the presenter will read the script faithfully. If the presenter tends to ad-lib, use video-outline-narration instead.
---

# Scripted Narration Video (v2)

The script is the source of truth: alignment only borrows *timing* from the
audio, so ASR word errors barely matter. The trade-off: **cue phrases must be
verbatim substrings of what is actually said** — ad-libbing breaks them
silently (this failure mode is why the v3 outline-driven skill exists).

## Prerequisites

Python 3.10+ with `faster-whisper`; `ffmpeg`; Chrome/Edge (cards); an NLE
importing FCP7 XML; optionally `pymupdf` if slides come from a talk PDF.
Transcription is compute-intensive: an NVIDIA GPU with 6 GB+ VRAM is
recommended (RTX 3070-class ≈ 2× real time); CPU-only is ~real time or
slower.

## Workflow

### 1. Script (human + agent)
A segment table: every block has an ID (`seg-01`…), an `[ON-CAM]`/`[VO]`
marker, the verbatim narration text, and an asset column whose **cue phrases
are exact substrings of the narration** ("at *fill in the year 2020* →
S10c"). Compute per-segment time targets from a measured reading rate
(record one segment, count characters/second, apply everywhere) — never
estimate by feel.

### 2. Record (human)
One file per segment, named by ID. Record picture even for [VO] segments.
Flub protocol: don't stop — pause, re-read the whole sentence (alignment
keeps the last clean take). Watch input level.

### 3. ASR (agent)
```
python scripts/asr_pass.py <clips...> --out analysis/asr
```
Defaults are the safe config. `--fast` (batched, no temperature fallback) is
tolerable here *only because* alignment coverage exposes dropped audio — if
a segment's coverage comes back low, rerun it with defaults and
`repair_gaps.py` before blaming the presenter.

### 4. Align (agent)
```
python scripts/align_narration.py <script.md> --out analysis/<video>-align.json
```
Character-level match of script ↔ ASR text (works for unspaced scripts like
Thai — no tokenizer needed). Output: per-segment speech spans, per-cue
timestamps with `ok/weak/missing` status, coverage %, and a deviation list.

**The review checkpoint is mandatory, not optional.** Expect coverage
55–90% with a lively presenter. For every `weak`/`missing` cue: join the ASR
tokens into one string, substring-search what was actually said, patch the
cue `t` by hand with `status:"manual"`. **Never rerun align_narration.py
after manual overrides without re-applying them — it overwrites.** Some
"deviations" are ASR mishearings, not real ad-libs; human eyes required.

### 5. Visuals (agent)
- Slides from a talk PDF: `scripts/build_slides.py <script.md> --pdf
  <talk.pdf>` — resolves each cue's slide reference to a page render, and
  emits `manifest.json`. "Hold" cues reuse the previous page.
- Generated cards: edit `CARDS` in `scripts/make_cards.py` (build states
  bind reveal steps to cue phrases), run it; it merges into the cue map.

### 6. Assemble
```
python scripts/build_narration_xml.py analysis/<video>-align.json \
    --out output/<video>.xml --overlays overlays/<video>
```
V1/A1 = segments trimmed to spoken spans; V2 = one image per cue, held to
reading time (cap ~16 s) then back to the presenter; markers carry coverage
and cue status (a red `!!` marker = a cue that never resolved — visible, not
silently missing). Validate paths before delivering.

### 7. Import + finish
FCP7 import always creates a new sequence. After the human starts manual
editing, deliver fixes as small patch XMLs positioned against *their
exported* timeline — never ask them to re-import a full regenerated rough.
