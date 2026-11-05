---
name: video-cut-audit
description: Executes frame-accurate, story-driven cuts anchored to the approved storyboard. Eliminates stutters, false starts, and background speech while protecting word boundaries with acoustic safety padding. Owns Gate 4.
---

# Cut Audit (Precision Story-Driven Editing)

> **Styles:** Editing pace & rhythm styles #173-187 of the 225-style catalog: `references/styles-pace-rhythm.md`.

A bad cut ruins good footage. The cut must be **anchored to the narrative storyboard approved at Gate 3**, maintaining narrative flow, eliminating dead air, and ensuring zero clipped syllables.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Dynamic Cutting & Pacing Rules

1. **Dynamic Style-Aware Cut Padding:**
   - Cut padding is **dynamic per video style, tempo (WPM), and narrative tension**, rather than fixed static offsets:
     - **Aggressive Hook / Fast-Paced Reel (180+ WPM):** `35ms - 50ms` lead-in, `60ms - 80ms` trailing tail. Eliminates conversational drag while preserving punch.
     - **Investigative Teardown / Forensic Breakdown (140-180 WPM):** `65ms - 85ms` lead-in, `95ms - 120ms` trailing tail. Balances fast information density with crystal-clear consonant articulation.
     - **Conversational Authority / Interview (110-140 WPM):** `100ms - 130ms` lead-in, `140ms - 175ms` trailing tail. Preserves natural breathing cadence and acoustic room resonance.
     - **Dramatic Verdict / Pause:** `80ms - 100ms` lead-in, `250ms - 350ms` trailing tail. Gives punchlines or shocking revelations room to breathe.
   - Never snap a cut directly to the speech detection threshold: doing so chops the initial acoustic burst of consonants (like 'P', 'T', 'K') and clips word endings.
2. **Audio Micro-Fades:**
   - Apply an **8ms - 15ms linear audio crossfade** at every edit boundary to eliminate digital clicks and DC-offset pops.
3. **Keep the Best Take (Retake Logic):**
   - When a creator repeats a sentence or phrase, keep the **last clean, confident take**, discarding false starts and stumbles.
4. **Dialogue vs. Non-Speaking Action:**
   - If footage contains visual actions (try-ons, demonstrations, reactions), cut each action at a natural motion inflection point (e.g. at the apex of a turn or smile).
   - Strip all ambient room chatter and non-creator speech during visual b-roll/cutaway shots.

---

## 2. Audio Waveform Dead-Air & Silence Scanning (Mandatory)

> [!WARNING]
> **ASR Stretching Trap:** Speech-to-text models (Whisper/ASR) automatically stretch word ending timestamps to swallow silences. Gaps between Whisper words will often appear as `0.0s` even when 1.5 seconds of dead air exist in the room tone!
> **Rule:** ALWAYS detect pauses via the **real audio waveform RMS energy** (`dead-air.py` or ffmpeg `silencedetect`), NEVER by word timestamp math alone.

1. **Audio Waveform Dead-Air Scan:**
   Run `"${VIDEO_SKILLS:-$HOME/.agents/skills}/video-cut-audit/scripts/dead-air.py"` or ffmpeg `silencedetect=noise=-30dB:d=0.35` across the audio track:
   - Identify all pauses > 0.40s between sentences and clauses.
   - Propose dropping the quiet core of each pause to tighten spacing to 0.25s - 0.30s.
   - Strip leading dead air before the first word (> 0.12s) and trailing dead air after the final word (> 0.15s).

---

## 2b. The cut toolchain (run in this order)

```bash
PY="$PROJECT/.venv/bin/python3"; CA="${VIDEO_SKILLS:-$HOME/.agents/skills}/video-cut-audit/scripts"; S="$ENG/scripts"
auto-editor "$W/raw/<clip>-clean.mp4" --edit audio:threshold=-30dB --margin 0.05s --export v1 -o "$W/speech.v1" --no-open
ffmpeg -y -v error -i "$W/raw/<clip>-clean.mp4" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$W/audio-raw.wav"
```

| Step | Tool | When / what |
|---|---|---|
| 1 | `"$S/paper-cut.py" --transcript "$W/transcript-raw.json" --duration <s> --speech "$W/speech.v1" --out-dir "$W"` | automatic cut: restarts, retakes (keeps the last clean take), false starts, silence → `cut-list.json` + `PAPER-CUT.md` |
| 1b | `"$S/stutter-scan.py"` | second opinion on step 1 (mechanical mistake finder) |
| 2 | `"$CA/hand-cut.py" --transcript … --speech "$W/speech.v1" --duration <s> --out-dir "$W" --keep A-B …` | **instead of step 1** when the story needs whole lines dropped (single take over the length budget), or paper-cut misread a list / slate / merged retakes. `A`/`B` = start of first / last kept word; `A-B!` keeps internal pauses |
| 3 | `"$CA/tighten-cut.py" --audio "$W/audio-raw.wav" --cut-list "$W/cut-list.json" --out "$W/cut-list-tight.json"` | trims lead-ins, tails and inner pauses by the waveform (ASR word starts sit up to 0.4 s early); segments with `"room_tone": true` are left alone |
| 4 | `"$CA/sliver.py" --cut-list "$W/cut-list-tight.json" --audio "$W/audio-raw.wav" --fix` | drops breath / tail slivers and moves heads/tails that carry a neighbouring word's sound |
| 5 | `"$S/edge-audit.py" --audio "$W/audio-raw.wav" --cut-list … --transcript "$W/transcript-raw.json" [--keeps keeps.args] --fix`, then again without `--fix` | every edge checked by RMS; must end with `0 issues`. On mid-sentence trims, inspect the 20 ms RMS around each edge yourself: Whisper word times can drift 0.3–0.6 s, so a "fixed" edge can still cut a word in half |
| 6 | `"$S/apply-cut.py" --input "$W/raw/<clip>-clean.mp4" --cut-list … --out "$W/hyperframes/input-video.mp4"` | frame-snapped flat cut + `cut-map.json` |
| 7 | re-transcribe the flat cut in 15 s windows (`video-transcribe`) | every kept word must be present; a missing or extra word = an edge problem, fix with `"$S/patch-cut.py"` and re-apply |
| 8 | `"$CA/cutlist-to-edl.py" --cut-list "$W/cut-list.json" --out "$W/cut-edl.json"` then `node "$CA/build-edl-review.mjs" "$W/cut-edl.json" --original <raw clip> --edited "$W/hyperframes/input-video.mp4" --output "$W/CUT-REVIEW.html"` | the Gate 4 review page for anything longer than a hook: kept vs cut on a timeline, largest cuts listed, original and edit side by side (click a red mark to hear what was removed) |

---

## 3. Gate 4: Interactive Cut & Dead-Air Review

Before applying the permanent cut or encoding video:
1. Generate `PAPER-CUT.md` listing:
   - **Total Original Duration vs. Proposed Cut Duration** (e.g. 80.2s raw -> 66.8s tight cut, dropping 13.4s of dead air).
   - **Dropped Pauses & Dead Air Table:**
     | Pause Start | Pause End | Duration | Context Before | Context After | Dropped |
     |---|---|---|---|---|---|
     | 0.00s | 1.27s | 1.27s | (clip start) | "to" | 1.15s dropped |
     | 3.24s | 4.84s | 1.60s | "tumhare" | "pas" | 1.30s dropped |
   - **Exact Timestamps of Kept Segments:** Kept range list with lead-in and trailing breath padding.
   - **Clean Transcript:** What the cut video will actually say.
2. Present `PAPER-CUT.md` to the user:
   > *"Here is the precision cut map eliminating all dead air. Original duration: 80.2s. Cut duration: 66.8s (13.4s of dead air eliminated across 12 pauses). Pacing is tightened to 165 WPM. Does this cut map look great?"*
3. Apply the cut with `apply-cut.py` only after user approval, writing **directly** to the composition folder:
   ```bash
   "$PROJECT/.venv/bin/python3" "$ENG/scripts/apply-cut.py" --input "$W/raw/<video>" \
     --cut-list "$W/cut-list.json" --out "$W/hyperframes/input-video.mp4"
   ```

> [!IMPORTANT]
> **Single Source of Truth (Zero Duplication)**: The conformed flat cut must be written directly to `$W/hyperframes/input-video.mp4` where HyperFrames reads it. Never duplicate or copy video files to `$W/input-video.mp4` or other folders.
