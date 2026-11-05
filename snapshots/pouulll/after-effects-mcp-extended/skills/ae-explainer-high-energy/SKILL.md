---
name: ae-explainer-high-energy
description: Make a 12–20 second high-energy motion-graphics promo for any product in Adobe After Effects through the After Effects MCP server. Fast beat-locked scene changes, kinetic typography, a shape that carries across every transition, a HUD frame, rendered with aerender and given a measured sound pass. Use when someone wants a hype reel, teaser, launch sting or showreel-style promo built in After Effects.
---

# High-energy explainer (After Effects)

A 12–20 second hype piece that hits like a showreel. Every half-second something lands on the beat, but it never feels like random cuts, because **a shape carries the eye across every transition**: a spark becomes a line, the line floods the screen into the next background, a full stop detaches and becomes the ball the next scene is built around.

You build it as an After Effects project with the MCP tools, render it with aerender and add sound with `ae-sound-effects`. **Load `ae-motion-core` first**: it has the build model, the tested expressions, how to check frames and how to render.

## Step 1: Get the brief (one message, then go)

Ask everything in **one** message, then work on your own. Only the product and the fonts are required; for anything else left blank, decide yourself and say what you chose.

1. **Product**: name, and what it does in a few sentences. A website URL is even better.
2. **The one thing** the viewer must remember (e.g. "type an idea, get a live app").
3. **Brand**: colours, logo file, or "use the website". If none, use the default palette below.
4. **Fonts**: which typefaces to use, and for what (a headline font for the slams, a secondary font for the human line and tagline, a small label font for the HUD and captions; one font for everything is fine). Offer 4–8 options from the fonts installed on this machine (see `ae-motion-core`, step 3) plus any brand fonts named on their website that are installed. This is the user's call: never pick a font for them, and don't start building text until they have chosen.
5. **Format**: 16:9 (1920×1080) or 9:16 (1080×1920). Default 16:9.
6. **Length**: default 15 s (128 BPM, 8 bars). Range 12–20.
7. **Music**: their own track (a file path), or a free track from the sound-effects skill's `MUSIC.md` (you suggest 2–3 that fit). Never synthesise music.
8. **Direction** (optional): scenes they want, a tagline, a call to action, anything to avoid.

If they gave a URL, read it (web fetch) for the product's real wording, features, colours and font names before writing anything (font names only to offer them as options). Use their real words for UI labels and taglines.

**Never invent facts.** No made-up customer counts, revenue, ratings, testimonials or quotes. Numbers only if the user or the website states them; otherwise use relative bars, progress and placeholder skeleton lines. Example content inside the UI (a prompt, a file name, a project name) is fine and should be believable; claims about the product itself (stats, user counts, ratings, offers like "free") are not. Calls to action use only a URL or offer the user or the website gave; with none, end on the name and tagline.

**Logos.** Use a logo only if the user supplies the file or it is their own product and they asked for it. Otherwise write the name as text in the headline font. Third-party logos only if supplied; otherwise neutral rounded tiles with the name.

## Step 2: Plan the scenes, then build

### The structure (6–8 scenes of 1.5–3 s, on a 120–140 BPM grid)

Write the beat sheet first: scene, start time on the beat grid, what carries in, what carries out, sound. Then put it in the main comp: `bpmMarkers` for the grid, and one comp marker per moment (`scene: …` or `sfx: <type> | <what happens>`).

1. **Spark open** (dark). Near-black canvas with a faint grid. A tiny accent mark appears, pulses, stretches into a thin horizontal line across the frame with a small label (`product / launch — 2026`), wobbles once, then the line **expands vertically into a full-screen flood** of the accent colour. That flood is the next background.
2. **Brand slam.** The product name in the headline font, all caps, huge, letters revealed on consecutive 1/16 beats, a small kicker above in the label font (`INTRODUCING — 2026`) and a line below in the secondary font (what it is, 2–4 words). The full stop or a letter's dot **detaches and grows** into the shape that starts the next scene.
3. **Kinetic triplet.** The value proposition as three short words or phrases, **two beats each** (three for the drawn-on word), each with its own treatment and background, swapped hard on the beat: dark on cream; accent on black with the word repeated as an outline pattern filling the frame; white on electric blue inside viewfinder corner brackets with a tiny `1920 × 1080` label; a last word that draws itself on. Each word enters with a fast blur/slide and lands with a slight overshoot.
4. **Signature visual.** One "how did they make that" moment that symbolises the product: a 3D field of cubes rippling from the centre, a particle flow that condenses into a ring and bursts outward, or a liquid blob morphing between shapes. Building blocks → cubes, data/AI → particles, flexibility → liquid. The camera tilts or orbits slowly while it plays.
5. **Product micro-moment.** One real interaction as a floating UI card, tilted slightly in 3D with two ghost cards behind it: the cursor flicks a toggle, presses the main button, a progress bar fills with a percentage, the button turns to `Done ✓`, a toast slides in. Use the product's real labels.
6. **Proof (only if real numbers exist).** A big count-up, a donut ring, staggered bars rising with one accent bar. No real numbers → skip it, or slam in the product's real capabilities as a list.
7. **Liquid/morph bridge.** The previous shape collapses to a dot, the dot becomes a ring pulse on dark, which becomes the dot in the logo.
8. **End card** (hold 2 s). Name with the accent dot, the tagline in the secondary font, a tracked line in the label font typing in (the real URL or call to action if given), a hairline rule.

Not every product needs every scene; 6 strong ones beat 8 weak ones. One idea per scene.

### Building each scene in After Effects

| Moment | Build it with |
|---|---|
| Grid background | Grid effect (`ADBE Grid`) on a solid at 6–10 % opacity, or a shape layer with Repeaters |
| Spark → line → flood | One shape layer: an ellipse that becomes a rectangle. Keyframe the rect's Size `[8,8] → [1920,2] → [1920,1080]` with hold keys and the **spring-between-keyframes** expression (`w 18, z 0.65`); Roundness from 4 → 0. The flood *is* the next scene's background: keep that layer and build the next scene on top |
| Letters on 1/16 beats | One text layer per word with a Range Selector animator (`textAnimatorPreset { preset: "cascadeIn" }`), or Opacity/Position animator offsets keyed on the beat; mask reveal = a rectangle mask per word with keyed Mask Path |
| Dot detaches and grows | A separate shape layer exactly over the full stop (place it with `getLayerBounds` on the text), spring Position + Scale into the next scene's hero shape |
| Hard swaps on the beat | Layers trimmed to start exactly on beat markers; the background colour is a solid per word |
| Outline pattern | Text layer with fill off, stroke on, repeated with Motion Tile (`ADBE Tile`) or a duplicated grid |
| Word drawing itself on | A stroke-only copy of the word revealed with Stroke (`ADBE Stroke`) "Reveal Painted", or Trim Paths on its outlines (`evalScript`: Layer > Create Shapes from Text) |
| Overshoot landings | Spring-between-keyframes, `z` ≈ 0.6–0.7 |
| Cube field | 3D solids in a grid (`proceduralLayout { mode: "grid" }`), Position Z and colour driven by `Math.sin(distance_from_centre / 80 - time * 6)`; a 3D camera with `cameraRigPreset { preset: "orbit" }` |
| Particle ring | CC Particle World (`CC Particle World`) with keyed birth rate/radius, or 60–120 small shape dots laid out with `generatePath` + `proceduralLayout`, scattered with seeded random and springing into a ring |
| Liquid blob | One shape path keyframed between outlines (`setShapePath` with `time`), plus Gaussian Blur + Simple Choker on an adjustment layer above it for the gooey merge |
| Floating UI card | Shape layers and text inside a precomp, 3D layer tilted 8–15°, two darker duplicates behind it offset in Z; `setupDOF` for depth |
| Count-up | Slider + the **count-up** expression; digit blur with Directional Blur (`ADBE Motion Blur`) |
| Typing line | The **typing** expression on Source Text |
| HUD frame | Corner brackets as shape paths, `SCENE 02 / 07` with the **scene counter** expression, a category label per scene, a running timecode (`timeToTimecode(time)`) with a red dot. 12–14 px, 50 % opacity, in a precomp on top of everything |
| Texture | Vignette (`CS Vignette`) and subtle Add Grain (`VISINF Grain Implant`) on an adjustment layer at the top; motion blur on |

### Rules that make it feel expensive

- **Transitions are objects, not cuts.** Every scene hands over through a shape (flood, a growing bar wipe, a dot that grows into the next background, a word that zooms through the camera). A hard cut between scenes only on a downbeat, at most twice.
- **Everything lands on the grid.** Big changes on beats, typography on 1/8 or 1/16 notes. Check it with `sampleProperty` at the beat times, not by eye.
- **HUD frame on every scene** (see above). It should feel like a camera viewfinder.
- **Type:** only the fonts the user chose in the brief, in the roles they chose them for.
- **Default palette:** ink `#0B0B10`, accent `#FF4F1A`, cream `#EDEBE4`, electric blue `#2F47FF`, white. The brand's main colour replaces the accent and its second colour replaces the blue.
- **Banned:** stock-template looks, glows on everything, emoji, more than 3 colours in one scene (not counting black and white), text too small to read at a glance, any scene without motion.

### Sound

128 BPM (or the user's track): punchy music, a riser into the brand slam and the end card, an impact on each flood, short ticks on each typed word, a whoosh on every carried transition, a pop on the end card. Mark each as an `sfx:` comp marker while you build (`sfx: impact | flood`, `sfx: whoosh | dot to scene 4`, `sfx: riser | into slam` with the marker's duration = the riser length). The sound pass places the sounds from these markers.

## Step 3: Check, render, deliver

Follow `ae-motion-core`:

1. **Stills.** `render-frame` at one time per beat-sheet row. Fix anything clipped, overlapping, unreadable, off-brand or empty. Check again.
2. **Numbers.** `sampleProperty` at every beat that should carry a hit: the change lands within a frame of the beat.
3. **Draft.** Render with Draft Settings to H.264 and send it to the user with the beat sheet; ask for changes before the final.
4. **Final.** Best Settings, motion blur on, silent H.264 (or ProRes). Say how long it will take before starting.
5. **Sound.** Run `ae-sound-effects` on the silent final with the music.
6. **Deliver** the saved AE project, the MP4 with sound, and a short note: the beat sheet, what is placeholder, the fonts used, and one alternative direction in a sentence.

Adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) `explainer-high-energy` skill (MIT).
