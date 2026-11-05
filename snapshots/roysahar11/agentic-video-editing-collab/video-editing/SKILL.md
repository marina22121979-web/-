---
name: video-editing
description: High-level workflow skill for video editing projects. Use when the user asks to edit, cut, assemble, or produce a video — especially short-form social media videos (Reels, Shorts, LinkedIn posts). Covers understanding source content (frames + transcription), planning, choosing between ffmpeg render and FCP XML round-trip with a professional NLE (Adobe Premiere Pro, DaVinci Resolve, etc.), iterating with the user, and platform output specs. References specific tool skills for syntax. Round-trip workflow tested with Adobe Premiere Pro.
allowed-tools: Read Bash Glob Grep
---

# video-editing

Umbrella workflow skill for collaborative video editing projects. The agent prepares structure (cuts, ordering, timing); a human refines visually inside a professional NLE. Choose the right tool for the task, iterate with the user, understand source content before cutting.

**This skill is the entry point.** Specific operations defer to focused skills:
- `/video-rotation-fix` — normalize rotated source files
- `/ffmpeg-editing` — ffmpeg editing operations (trim, concat, speed, fade, scale)
- `/fcp-xml` — generate FCP 7 XML timelines for import into a professional NLE
- `/ffmpeg-gif` — standalone GIF generation (not editing)
- `/transcribe` — speech-to-text with timestamps (separate repo: [transcribe-skill](https://github.com/roysahar11/transcribe-skill))

**Tested with Adobe Premiere Pro** as the human-side editor. The FCP XML workflow should also work with DaVinci Resolve, Final Cut Pro 7, and other apps that import xmeml v5, but those paths haven't been verified.

## Workflow phases

**1. Understand source content** — extract frames + transcribe audio to build a mental model of what's in each clip. Don't skip this; frame-only analysis misses dialogue, and transcription-only misses visual moments.

**2. Understand goal** — target platform, duration, aspect ratio, audience, narrative arc, tone. Clarify with the user before proposing cuts.

**3. Plan the edit** — propose a cut structure (which clips, which order, in/out points, timing). Use a table or structured format so the user can redirect before implementation.

**4. Iterate** — build, preview, adjust. Choose the right tool:
   - Quick rough cut / preview → `/ffmpeg-editing`
   - Visual refinement needed / frame-accurate adjustments / collaborative work / final polish → `/fcp-xml` (hand off to a professional NLE)
   - Both: iterate structure in chat via ffmpeg, then generate XML for NLE finishing

**5. Polish** — color grading, fine motion, effects, final audio mix — belongs in the NLE, not in chat. Our role ends with structural correctness.

## Initial source inspection (always)

When you first encounter a set of video files for a new editing project, before any cutting work:

1. **Probe dimensions, duration, fps** for every file:
   ```bash
   ffprobe -v quiet -show_entries stream=width,height,r_frame_rate \
     -show_entries format=duration -of json "clip.mp4"
   ```

2. **Check for rotation metadata** — phone footage often has Display Matrix rotation that NLE FCP XML import ignores. If any clips have rotation, use `/video-rotation-fix` to verify and normalize *before* any other work. Skipping this step creates sideways clips that are painful to fix later.

3. **Understand content** — see "Understanding video content" below.

4. **Note duplicates** — messaging apps often save the same video under different IDs. Check by duration + visual content.

## Understanding video content

Handheld and phone videos have rapid camera movement. Frame-only analysis misses most of what's happening between frames. Cross-reference visual + audio:

### Frame extraction (adaptive interval)

```bash
dur=$(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$f" | cut -d. -f1)

if [ "$dur" -lt 15 ]; then fps="1/3"       # every 3s for very short
elif [ "$dur" -lt 60 ]; then fps="1/5"     # every 5s for short
elif [ "$dur" -lt 300 ]; then fps="1/15"   # every 15s for medium
else fps="1/30"; fi                        # every 30s for long

mkdir -p frames
ffmpeg -v quiet -i "$f" -vf "fps=${fps}" -q:v 3 frames/frame_%03d.jpg
```

Read the extracted frames with the Read tool to understand what's visually in the clip.

### Transcription

Use `/transcribe` for Hebrew (uses ivrit-ai models) or other languages. Produces SRT + JSON with word-level timestamps. Essential for:
- Identifying quotable moments by exact timecode
- Understanding dialogue and reactions
- Planning cuts around speech boundaries

### Cross-reference

After frame extraction + transcription, build a short per-clip catalog: what's visually happening, who's speaking, what they're saying, any key moments with timestamps. This becomes the raw material for planning the edit.

## Tool selection: ffmpeg vs FCP XML round-trip

| Need | Tool |
|---|---|
| Fast preview, no visual polish required | `/ffmpeg-editing` |
| Final polished output with color / effects | `/fcp-xml` → NLE (Premiere, Resolve, etc.) |
| Collaborative review and feedback | `/fcp-xml` (NLE's collaboration features — e.g., Premiere Team Projects, Frame.io) |
| Iterating structure (which clips, order, timing) | Either — ffmpeg is faster for rough cuts |
| Adding captions with Hebrew RTL | ffmpeg with `ass` filter (requires `ffmpeg-full`) OR the NLE |
| Quick format conversion, trim, scale | `/ffmpeg-editing` directly |
| Multi-track audio mix with fine control | NLE (via `/fcp-xml`) |
| Scale/position/effects | NLE (FCP XML can carry basic scale; complex effects applied in the NLE) |

**Typical workflow** for a real edit: iterate structure in chat using ffmpeg previews → once structure is approved, generate FCP XML → user imports to their NLE → refine visually → export FCP XML back if structural changes are needed → iterate again.

## Editing concepts

Brief conceptual reference. For syntax, see `/ffmpeg-editing` and `/fcp-xml`.

- **Trim**: use specific in/out points in source. Always prefer exact timestamps over "approximately." For conversation cuts, round to speech boundaries from the transcript.
- **Concat**: linear concatenation of clips. Different aspect ratios need scale+pad logic. Different frame rates may need normalization before concat.
- **Speedup / slowdown**: condenses or stretches time. Decide whether audio pitch should track speed (the default for ffmpeg) or be preserved (handled inside the NLE, not in FCP XML — requires manual application after import). See `/ffmpeg-editing` and `/fcp-xml` for syntax.
- **Fade**: in / out / cross-dissolve. In FCP XML, all three are `<transitionitem>` with `Cross Dissolve` and varying `alignment`. In ffmpeg, use `fade` filter or `xfade`.
- **Scale/pad for target aspect ratio**: never squish. Either scale-to-fit (letter/pillarbox) or scale-to-fill (crop). For social media content, scale-to-fill typically looks better; for preserving the full frame, scale-to-fit.

## Platform output specs

| Platform | Aspect | Resolution | Duration | Notes |
|---|---|---|---|---|
| Instagram Reels | 9:16 | 1080x1920 | ≤90s | Vertical, under 60s for best reach |
| TikTok | 9:16 | 1080x1920 | ≤3min | Vertical, 15-60s sweet spot |
| YouTube Shorts | 9:16 | 1080x1920 | ≤60s | Vertical |
| LinkedIn feed | 4:5 portrait | 1080x1350 | 30-90s | Optimal engagement, mobile-friendly |
| LinkedIn landscape | 16:9 | 1920x1080 | — | Less mobile-friendly |
| YouTube regular | 16:9 | 1920x1080 | — | H.264 + AAC, wide compatibility |
| X (Twitter) | 16:9 or 1:1 | 1280x720 or 1080x1080 | ≤2:20 | — |

For **mixed aspect ratio sources** in a single target output, pick a target aspect ratio for the sequence and handle each source with scale+pad appropriate to its orientation (portrait→pillarbox in 16:9, landscape→letterbox in 9:16, etc.).

## Planning a short-form social media edit

When the user describes a short-form video project (Reel / Short / LinkedIn), the planning checklist:

1. **Hook** — what grabs attention in the first 2-3 seconds? Cold open with a reaction, a line, or a visual — don't lead with title cards on social media.
2. **Narrative arc** — what's the through-line? Process → reveal → reaction → takeaway is a common pattern.
3. **Pacing** — social media cuts are fast. 3-5 second average clip length, shorter for energy peaks.
4. **Captions** — not word-by-word (distracting). Short phrases on key lines. Remember: most users scroll with sound off on first pass.
5. **"Sound on" indicator** — when audio is essential, include a visual prompt to turn sound on.
6. **CTA** — link, handle, or next step at the end.

## Iteration patterns

### Iterating in chat via ffmpeg preview
1. Propose cut structure as a table (clip, source, in/out, label).
2. Get user approval on the structure.
3. Render a quick preview with `/ffmpeg-editing` at lower resolution for speed.
4. User watches, gives notes.
5. Adjust the cut list, re-render.
6. Repeat until structure is right.

### Handing off to the NLE
1. Once structure is approved, generate the FCP XML via `/fcp-xml`.
2. User imports into their NLE (in Premiere: File > Import; other NLEs have similar import paths).
3. User refines visually — color, fine motion, effects, final audio.
4. If structural changes emerge during refinement, user exports FCP XML back (in Premiere: `File > Export > Final Cut Pro XML`) and we parse with OTIO to continue iterating in chat.
5. Structural changes → update our state, regenerate XML, user re-imports to a new sequence (preserving their NLE-side refinements in the old sequence for reference).

### Round-trip limitations
Read `/fcp-xml` for the full list. The summary: **structural information round-trips cleanly** (clips, timing, order, linking, explicit scale/speed/fades). **Refinements added inside the NLE do not** (color grading, advanced effects, fine motion adjustments, pitch preservation).

Design implication: iterate structure with me, apply refinement in the NLE, don't expect refinement to survive a round-trip back to chat. When you come back for a structural change, the new XML creates a new sequence; manually copy any refinement you want to preserve.

## Anti-patterns

- **Jumping straight to cuts without understanding the source**: leads to missing the best moments and making cut decisions based on thumbnail guesses.
- **Frame-only analysis of handheld footage**: misses everything between frames. Always combine with transcription.
- **Blindly normalizing rotated files**: always verify visually first. See `/video-rotation-fix`.
- **Using ffmpeg for final polish**: you'll spend hours fighting filter syntax for things a professional NLE does in two clicks. Hand off to the NLE for refinement.
- **Using the NLE for rough cuts in iterative chat work**: too slow. Use ffmpeg previews.
- **Word-by-word captions**: typographically ugly and distracting. Use short phrases on key lines.
- **Starting with a static title card on social media**: kills the hook. Open with action or a reaction.
- **Hardcoding scale/position in FCP XML without user discussion**: those are creative decisions. Unless asked, leave scale at "fit source to frame" defaults and let the user refine in the NLE.
