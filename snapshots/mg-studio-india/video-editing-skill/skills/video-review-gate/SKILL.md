---
name: video-review-gate
description: Final quality gate on the rendered deliverable - checks structure, speech alignment, loudness, and frame sheets. Verifies CLI check report and renders, keeping composition fully editable via CLI tools, and automatically purges transient temp files. Owns Gate 6.
---

# Review Gate & Delivery (Final Quality Assurance)

Inspects the final deliverable from the viewer's perspective. Guarantees visual polish, acoustic fidelity, CLI composability, and complete temp file cleanup.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
F="$W/processed/<project>-v<N>.mp4"
```

---

> [!IMPORTANT]
> **Virtual Environment (STRICT)**: ALWAYS execute scripts using the project's virtual environment (`"$PROJECT/.venv/bin/python3"`). Never invoke system python.

Run verification on the rendered MP4 file:
```bash
"$PROJECT/.venv/bin/python3" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-review-gate/scripts/review.py" --final "$F" --preset shorts --res 1080x1920 \
  --storyboard "$W/storyboard.json" --transcript "$W/transcript.json"
```

Must verify:
1. **Structure & Resolution:** Exact 1080x1920 vertical canvas, 12+ Mb/s bitrate, BT.709 color tags.
2. **Audio Loudness:** `-14.0 LUFS` integrated, `<= -1.0 dBTP` true peak.
3. **No Black Frames or Glitches:** 0 frame dropouts, 0 flash artifacts.
4. **Platform Safe Zones:** Text clear of bottom 320px and top 180px.

---

## 2. CLI Composition Inspection & Interactive Preview

Validate the HyperFrames composition using CLI tools without requiring the desktop GUI app:
```bash
npx hyperframes check "$W/hyperframes"
```
Optional interactive preview via local browser server (on user request):
```bash
npx hyperframes preview "$W/hyperframes"
```
Keeps the project 100% editable, composable, and verifiable via command line.

---

## 3. Data Integrity & Workspace Preservation

By default, core project directories (`preview/`, `audio_processing/`, and `hyperframes/`) are preserved intact inside the project directory so the creator can inspect color grade sheets, audio waveforms, Whisper ASR outputs, and editable compositions.

Only when the creator explicitly requests a production disk purge:
```bash
"$PROJECT/.venv/bin/python3" "$ENG/scripts/clean-temp.py" "$W" --clean-reports
```
This safely removes transient scratch dumps while protecting the master video deliverable (`processed/<project>-v<N>.mp4`).
