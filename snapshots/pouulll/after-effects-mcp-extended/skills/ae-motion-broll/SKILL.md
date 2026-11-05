---
name: ae-motion-broll
description: Turn a talking-head video and its transcript into motion-graphic B-roll timed to the speaker's words, built in Adobe After Effects through the After Effects MCP server - one shape that morphs and never cuts, driven by a cursor, with spring motion. Delivers an After Effects project with every clip placed on the speaker's timeline, rendered clips (ProRes with alpha for panels) and a preview render. Use when someone gives a video (and ideally a transcript) and asks for motion graphics, B-roll, animated cutaways or overlays made in After Effects.
---

# Motion B-roll (After Effects)

You make motion-graphic clips for a creator's video. Every clip is **one shape that never cuts**: it morphs its size, corners and colour from state to state while its content swaps with a short blur. A cursor drives the changes with real clicks and drags, and every change lands on a spoken word.

The output is an After Effects project: the speaker's video in a master comp with every clip already placed on its words, each clip as its own comp, the rendered clips the creator can drop into their editor, and a preview render. **Load `ae-motion-core` first**: it has the tested expressions and how to check and render.

`$SKILL` below means this skill's folder. Work in a `motion/` folder in the user's project.

## 1. Set up

Needs Python 3, ffmpeg and After Effects with the MCP bridge connected (`bridge-status`). For word timestamps from audio: `pip install faster-whisper` (optional).

## 2. Interview

Use the AskUserQuestion tool; keep it to one round. You need:

- **The video.** A path.
- **The transcript.** An SRT or VTT with timestamps is best. With plain text only, get word timestamps from the audio (faster-whisper) or ask for an SRT.
- **Density:** light (2–4 clips per minute, only the strongest moments), medium (default, 4–7 per minute) or heavy (most lines covered, with short gaps of face).
- **Look:** the default palette (warm gray canvas, black and white components, one orange accent), or their brand (ask them to drop a logo, screenshots or brand colours into `motion/inputs/`, and read those).
- **Fonts**: which typefaces to use, and for what (UI text, and a code font for terminals and file names if the video needs one). Offer 4–8 options from the fonts installed on this machine (see `ae-motion-core`, step 3) plus any brand fonts named on their website that are installed. This is the user's call: never pick a font for them, and don't start building text until they have chosen.
- **Anything to avoid or include.** Lines to leave on their face, real numbers or names to show, product screenshots to recreate.

Skip any question the user already answered.

## 3. Inspect the footage

```bash
python3 $SKILL/scripts/inspect_video.py <video> motion/work
python3 $SKILL/scripts/words.py transcript.srt > motion/work/words.txt   # .vtt works too
```

Look at `motion/work/contact.png` yourself. `video.json` gives resolution, fps and layout sections:
- **full:** the speaker fills the frame.
- **pip:** the speaker is in a box and the rest is empty, with the box position and a warning if it changes size or moves.
- **black:** the whole frame is black (a fade, intro or outro).

Word times from an SRT or VTT are estimates (±0.2 s); treat them as such.

Then set up AE: `importFootage { path: <video> }`, and `buildComposition` a master comp `MASTER` at the video's exact size, frame rate and duration with the video as its bottom layer (`addFootageToComp`). Put one comp marker per transcript cue (`setMarker`, comment = the line) so the words are visible on the timeline.

## 4. Plan, and get approval before building

Show a table with one row per clip:

| # | In–Out | The line it covers | What the shape does, on which words | Treatment | Why |

**Creative direction: decide how much of the frame each clip takes.** This is the most important call; make it per clip and give the reason.

- **Full-frame cutaway.** The frame is all speaker, and the line describes something to *see*: a product, a process, a comparison, a number, a chapter change. Cut away for the length of the idea (3–10 s), then give the face back. Not in the first second of the hook, not on personal, emotional or opinion lines. At least ~2 s of face between cutaways.
- **Panel in the empty space.** The edit already leaves room: a PiP box, a split, a plain region. A transparent clip centred in the empty area, sized to stay clear of the speaker's box at every moment. It can run long (15 s+) as one continuous morph, because the speaker stays on screen. If `inspect_video.py` reports the box changing, ask whether that's intended, then size for the largest box or split the panel at the change.
- **Nothing.** The line is about the speaker, or it's too close to another clip.

**Content rules:**
- Show the subject's real objects: the folder, the terminal, the file, the product, the result. Pull them from the words. Map each idea onto an interaction: pill + click, progress, check, status island, card with a drag, slider, toggle, tabs, chart + tooltip, search/filter, file drag-and-drop, terminal typing, side-by-side comparison, chapter card.
- **Never invent numbers, quotes, prices or results.** Use relative bars, skeleton text lines or labels taken from the transcript, and list what is illustrative. Real figures only when the user gives them.
- One idea per clip. A continuous stretch (a whole PiP section) can be one long clip with several states.
- Pace to speech, not music: one change per spoken beat, about 0.4–1.2 s apart.

Wait for the user to approve or edit the plan.

## 5. Build each clip as a comp

One comp per clip, named `NN-name`, at the video's size and frame rate, duration = out − in. Clip-local time = word time − clip in-point.

| Element | Build it with |
|---|---|
| **The one shape** | One shape layer `Shape` with a rounded rectangle and a fill. Keyframe the Rectangle Path's **Size** and **Roundness** and the Fill **Color** with hold keys, one per state, each on its word; put the **spring-between-keyframes** expression (`w 14, z 0.82`) on all three, so every state change is one physical morph. Keep a state's key a frame before its word so the morph lands on it |
| **Camera zoom per state** | All clip content in a precomp; in the clip comp keyframe its Scale (hold keys per state: roughly 120–160 % for cards, 180–220 % for pills) with the spring expression (`w 8, z 1`). Collapse Transformations on so text stays sharp |
| **Content per state** | One text/shape layer (or small precomp) per state, trimmed to the time it is visible, with the **content swap** expressions on Opacity and Gaussian Blur: exit blurs out fast, entry waits so old and new never overlap |
| **Content riding an edge** | A null with the **pin to the shape's top edge** expression below; parent top-anchored content to it so it rides the edge as the shape grows |
| **Stretchy indicator** (levels, tabs, effort) | The **stretchy indicator** recipe: leading edge `w 22`, trailing edge `w 10` |
| **Cursor** | A macOS-style arrow, constant size on screen (put it in the clip comp, above the zoomed precomp), Position keys on gentle curves arriving a beat before each click; a press dip (Scale spring, `w 22`) and a soft ripple on the clicked control |
| **Typing** | The **typing** expression (terminals in the code font from the interview) |
| **Rows or bars on words** | Per row: trimmed to its word, content swap for opacity, width from the spring expression; stagger with `staggerLayers` |
| **Direct manipulation** (slider, drag) | While the cursor is held, the value follows the cursor's Position (expression reading the cursor layer); on release it springs from where it was |
| **Transparent panel** | No background layer; light shapes (`#F4F2EE`) so they read on dark footage |

```js
// Pin a point to the morphing shape's top edge (content parented to this null rides the edge as the shape grows).
var shape = thisComp.layer("Shape");
var rect = shape.content("Group 1").content("Rectangle Path 1");
var c = rect.position, s = rect.size, offset = 24;   // px below the top edge
shape.toComp([c[0], c[1] - s[1] / 2 + offset]);
```

Then place each clip comp into `MASTER` at its in-point (`addFootageToComp { compName: "MASTER", itemName: "NN-name", startTime: <in> }`), above the speaker video. Full-frame cutaways cover the speaker; panels sit over the empty space.

## 6. Check stills on the key words

`render-frame` on the **clip comp** at each state's settled time and a couple of mid-morph moments, then on `MASTER` at the same moments to see the clip over the footage. Look at every one. Fix anything cramped, clipped, unreadable or off-word, or where the cursor leaves the frame. Check panels against the largest speaker box. Then check once more.

## 7. Render

Each clip: `addToRenderQueue { compName: "NN-name", ... }` then `start-render`.
- Full-frame clips: H.264 (or `High Quality`) at the video's fps, `.mp4`/`.mov`.
- Panel clips: an alpha output module (`High Quality with Alpha` or a ProRes 4444 template; `listRenderQueue` shows what this machine has) to `.mov`.
- Name each file by its timeline in-point: `NN-name_0m32s40.mov` = 0:32.40.
- Preview: render `MASTER` (Draft Settings is fine) to `preview.mp4`, with the original audio.

## 8. Deliver

All in `motion/out/`:
- the clips
- `TIMING.md`: file, in, out, the line it covers, the treatment, and what is illustrative
- `preview.mp4`: their video with the clips cut in
- the saved AE project: `MASTER` with every clip on its words, each clip comp editable

Say plainly that the preview is for review: for the final cut they place the clips in their own editor (or finish in the AE project), where they can nudge timing, add transitions and mix audio. If they want sound on the clips, run `ae-sound-effects` on the preview with cues from the clips' state changes.

## Style defaults

The user's brand overrides these.

- **Colour:** canvas `#E9E7E2`, ink `#0B0B0B`, white components, one accent `#FF5A1F`. Panel clips on dark footage use light shapes (`#F4F2EE`).
- **Type:** the fonts from the interview.
- **Icons:** one icon set with one stroke weight (draw icons as shape paths, e.g. traced from Lucide, ISC licence).
- **Motion:** springs with a tiny overshoot at most. Leading and trailing edges ride different springs so indicators stretch. The camera zooms so each state fills the frame.
- **Banned:** bouncy easing, particles, glows, gradients on UI chrome, mixed icon strokes, dead time, anything that looks like a template, made-up data.

## Gotchas

- Collapse Transformations on any precomp the camera scales up; otherwise text renders soft.
- Text swapping inside a morphing shape needs its own enter and exit timing (content swap expression), or the old and new text overlap.
- Items that slide under a highlight need a faster spring than the highlight, or the highlight row sits empty for a moment.
- Keep the cursor inside the frame at every zoom, including during morphs: check with `getLayerBounds` on the cursor at the extremes.
- Word estimates from an SRT drift within a cue; put important changes on the first or last word of a cue when you can.
- A clip ends by holding its last state; extend its comp if its slot in `MASTER` is longer.

Adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) `motion-broll` skill (MIT); `scripts/inspect_video.py` and `scripts/words.py` are his.
