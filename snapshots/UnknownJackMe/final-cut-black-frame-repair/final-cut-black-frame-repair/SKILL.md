---
name: final-cut-black-frame-repair
description: Audit and safely repair abnormal black flashes in Final Cut Pro FCPXML/FCPXMLD projects and exported MP4/MOV videos, especially when subtitles are already burned into the pixels. Use for clip-boundary black frames, explicit or implicit timeline gaps, source-edge/render-only black frames, burned-subtitle preservation, frame/PTS-preserving donor replacement, FCPXML safety copies, candidate previews, and complete video/audio/XML/hash validation.
---

# Final Cut Black Frame Repair

Execute the workflow; do not merely recommend commands. Treat the source video and FCPXMLD as immutable.

## Required tools and resources

Require `ffmpeg`, `ffprobe`, `python3`, and `xmllint`. Prefer NumPy and Pillow for image analysis. If the active Python lacks them in Codex Desktop, call `codex_app.load_workspace_dependencies` and use the bundled Python. Do not install optional packages unless the user authorizes it.

Resolve all bundled paths relative to this `SKILL.md`:

- `scripts/audit_fcpxml.py`: exact Fraction-based FCPXML audit.
- `scripts/scan_video.py`: real-PTS media scan, subtitle ROI estimation, candidate JSON, and previews.
- `scripts/repair_video.py`: approved donor-frame replacement and conservative FCPXMLD copying.
- `scripts/validate_video.py`: frame/PTS/audio/decode/XML/hash/subtitle validation.
- Read [references/classification-and-safety.md](references/classification-and-safety.md) before classifying or approving repairs.
- Read [references/output-contract.md](references/output-contract.md) before creating the final output tree or report.

## Non-negotiable safety

1. Hash every source before audit and again after validation.
2. Never modify or overwrite a source, FCP Library, or source Bundle.
3. Never automate the Final Cut Pro GUI.
4. Never delete frames, shorten the timeline, force CFR, or globally remove black content.
5. Never OCR, recreate, reorder, crop, or add another subtitle layer.
6. Use crop only for detection.
7. Preserve every input video PTS and every audio packet whenever possible.
8. Stop automatic repair for ambiguous subtitles, subtitle transitions, complex timelines, HDR/bit-depth uncertainty, or audio-sync risk.
9. Keep temporary frames and filters under the requested output `work/` directory.
10. Do not declare PASS until validation independently proves it.

## Phase 1: inventory and pairing

1. Confirm each video and FCPXML/FCPXMLD exists.
2. For a Bundle, find `Info.fcpxml`; otherwise find the unique `.fcpxml` entry.
3. Record type, size, permissions, mtime, and SHA-256.
4. Record tool versions and required FFmpeg filters: `blackdetect`, `blackframe`, `freezeframes`, `crop`, `signalstats`, `metadata`, `select`, `blend`, and `overlay`.
5. Do not trust filenames alone. Pair project and export using all available evidence:
   - project name and language;
   - FCPXML sequence duration;
   - video duration and frame count;
   - visible burned-subtitle language.
6. If the proposed pair differs by more than one frame or project labels conflict, report the mismatch and block repair until the pair is corrected.

## Phase 2: read-only audit

Create the output tree from `references/output-contract.md`, then run:

```bash
python3 scripts/audit_fcpxml.py \
  --fcpxmld "/path/Project.fcpxmld" \
  --project "Project Name" \
  --output "/path/output/work/Project/fcpxml_timeline_audit.json"

python3 scripts/scan_video.py \
  --video "/path/export.mp4" \
  --timeline "/path/output/work/Project/fcpxml_timeline_audit.json" \
  --work "/path/output/work/Project" \
  --previews "/path/output/previews/Project"
```

Use the same Python executable for both commands.

The scripts must produce:

- complete ffprobe input JSON;
- frame-level real PTS data and CFR/VFR result;
- main-spine elements, exact Fraction times, gaps, discontinuities, boundaries, and complexity flags;
- dynamic subtitle ROI estimated independently per video;
- whole-frame and content-ROI black metrics;
- blackdetect/blackframe logs;
- each candidate’s `candidate.json`, annotated frames, and Contact Sheets;
- an unapproved `repair_plan.json`.

Inspect every candidate preview yourself. Override heuristic classifications only with recorded visual evidence.

## Phase 3: classify and approve

Apply the taxonomy and donor rules in `references/classification-and-safety.md`.

Edit only the generated `repair_plan.json`:

- Set `approved: true` only for TYPE_A, TYPE_B, TYPE_C, or evidence-rich TYPE_D.
- Keep TYPE_E and TYPE_F unchanged.
- Keep TYPE_G and TYPE_H unapproved and mark manual review.
- Record one donor per range or `split_donors` around a cut.
- Record the subtitle classification and why the donor preserves it.
- Require `SUBTITLE_NONE`, `SUBTITLE_MATCH_PREVIOUS`, `SUBTITLE_MATCH_NEXT`, or `SUBTITLE_MATCH_BOTH` for full-frame replacement.
- Do not approve `SUBTITLE_TRANSITION` or `SUBTITLE_AMBIGUOUS`.

Finish this audit and approval artifact before any repair.

## Phase 4: repair new files

Run:

```bash
python3 scripts/repair_video.py \
  --video "/path/export.mp4" \
  --plan "/path/output/work/Project/repair_plan.json" \
  --output-video "/path/output/video/Project_blackframe_repaired.mp4" \
  --fcpxmld "/path/Project.fcpxmld" \
  --project "Project Name" \
  --output-fcpxmld "/path/output/fcpxml/Project_NO_BLACK_GAPS.fcpxmld"
```

The script refuses unsafe or unapproved entries. It replaces frames without changing frame count or PTS, stream-copies audio, preserves color metadata, and creates a conservative FCPXMLD copy with the selected project renamed `_NO_BLACK_GAPS`.

Do not structurally close an FCPXML gap when `timeMap`, retime, transition, multicam, compound clips, connected storylines, connected titles/captions, or continuous connected audio make the change unsafe. A conservative importable copy plus repaired MP4 is the correct outcome.

For a simple structural edit, modify only the copied XML, preserve UIDs and resource references, then run `xmllint --noout` and repeat the Fraction timeline audit.

## Phase 5: validate independently

Run:

```bash
python3 scripts/validate_video.py \
  --input-video "/path/export.mp4" \
  --output-video "/path/output/video/Project_blackframe_repaired.mp4" \
  --plan "/path/output/work/Project/repair_plan.json" \
  --input-manifest "/path/output/work/Project/input_manifest.json" \
  --output-fcpxml "/path/output/fcpxml/Project_NO_BLACK_GAPS.fcpxmld" \
  --work "/path/output/work/Project/validation"
```

Additionally:

1. Fully decode the output.
2. Compare video frame count, real PTS sequence, duration, dimensions, SAR/DAR, frame rate, pixel format, color metadata, and time base.
3. Compare all audio packet PTS/DTS/duration/size/flags exactly when audio was copied.
4. Rerun whole-frame and content-ROI black detection.
5. Recheck every FCPXML boundary ±3 frames.
6. Verify repaired locations are non-black and no new black runs exist.
7. Compare output subtitle masks to the approved donor and inspect before/after subtitle Contact Sheets.
8. Validate XML and all nonnegative time attributes.
9. Rehash every original source and compare with the initial manifest.

If any required check fails, use the corresponding FAIL verdict from the output contract.

## Phase 6: report

Create one report per project using `references/output-contract.md`. Include the corrected input pairing, every candidate and donor, structural risks, exact input/output comparisons, source hash recheck, and final verdict.

Use `PASS_BURNED_SUBTITLE_VIDEO_REPAIRED_DURATION_PRESERVED` only when:

- every confirmed abnormal black range is repaired;
- frame count, PTS, duration, and audio timing are preserved;
- burned subtitles are visually and metrically preserved;
- normal black content remains;
- output fully decodes;
- XML validates;
- source hashes are unchanged.

Explicitly state when the MP4 is repaired but the conservative FCPXMLD copy retains complex nested gaps that could reappear on a new Final Cut render.
