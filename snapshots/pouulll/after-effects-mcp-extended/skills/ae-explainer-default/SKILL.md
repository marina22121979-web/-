---
name: ae-explainer-default
description: Make a clean 45–90 second product demo video for any software product in Adobe After Effects through the After Effects MCP server. Airy light canvas, short centred lines the camera pushes into, the product's own UI rebuilt as vector layers and shown up close as it is used (typing, results, tables, clicks), integrations, and a logo close, rendered with aerender and given a measured sound pass. Use when someone wants a product demo, launch video, feature walkthrough or "how it works" video built in After Effects.
---

# Default explainer (After Effects)

A calm, premium product demo, the kind a well-funded startup puts on its homepage. Its whole trick is restraint: a bright, airy canvas, one short line of text at a time, and the product's own interface rebuilt cleanly and filmed **up close** while it is being used. The camera does the storytelling: it pushes into a line of text, rides along with typing, pulls back to reveal the result, and glides to the next feature.

You build it as an After Effects project with the MCP tools, render it with aerender and add sound with `ae-sound-effects`. **Load `ae-motion-core` first**: it has the build model, the tested expressions, how to check frames and how to render.

## Step 1: Get the brief (one message, then go)

Ask everything in **one** message, then work on your own. Only the product and the fonts are required; for anything else left blank, decide yourself and say what you chose.

1. **Product**: name, and what it does in a few sentences. A website URL is even better.
2. **The one thing** the viewer must remember.
3. **Brand**: colours, logo file, or "use the website". If none, use the default palette below.
4. **Fonts**: which typefaces to use, and for what (title lines, UI text; usually one family in two or three weights). Offer 4–8 options from the fonts installed on this machine (see `ae-motion-core`, step 3) plus any brand fonts named on their website that are installed. This is the user's call: never pick a font for them, and don't start building text until they have chosen.
5. **Format**: 16:9 (1920×1080) or 9:16 (1080×1920). Default 16:9.
6. **Length**: default 60 s. Range 45–90.
7. **Music**: their own track, or a free track from the sound-effects skill's `MUSIC.md` (you suggest 2–3 that fit). Never synthesise music.
8. **Features**: the 3–5 features or workflow steps to show, and anything the product connects to (integrations). With a URL, take these from the site.
9. **Direction** (optional): scenes they want, a tagline, a call to action, anything to avoid.

If they gave a URL, read it (web fetch) for the product's real wording, features, colours and font names before writing anything (font names only to offer them as options). Use their real words for UI labels and taglines.

**Never invent facts.** No made-up customer counts, revenue, ratings, testimonials or quotes. Numbers only if the user or the website states them; otherwise use relative bars, progress and placeholder skeleton lines. Example content inside the UI (a prompt, a file name, a project name, prices on a receipt) is fine and should be believable; claims about the product itself are not. Calls to action use only a URL or offer the user or the website gave; with none, end on the name and tagline.

**Logos.** Use a logo only if the user supplies the file or it is their own product and they asked for it. Otherwise write the name as text in the chosen font. Third-party logos (integrations) only if supplied; otherwise neutral rounded tiles with the name.

Budget by length (drop optional sections first):

| Length | Features | Optional sections |
|---|---|---|
| 45 s | 2–3, about 9 s each | proof or integrations, not both |
| 60 s | 3–4, about 10 s each | one of proof / integrations |
| 90 s | 4–5, about 12 s each | both |

## Step 2: Write the script, then build

### The structure

Write the script and beat sheet first: every line of on-screen text, which UI moment follows it, and its time; add the times up against the budget. On-screen text is the only "voice", so it has to tell the story by itself. Put the beat sheet into the main comp as comp markers.

**How scenes and camera fit together:** each scene (a title line, a UI moment) is its own **precomp with its own camera move**. Inside a scene the camera pushes, rides and pulls back; between scenes the outgoing precomp dissolves with a short blur (0.3–0.4 s) into the next one, which is already moving (overlap the two layers in the main comp).

1. **Open (0–5 s).** Plain light canvas. A small word fades up in the centre: `Introducing`. It dissolves into the brand moment: the soft brand gradient sweeps in (silk-like diagonal light bands drifting slowly) with the logo or name centred, small.
2. **The problem or the ask (≈5 s).** A short line the viewer recognises (`Still building prospect lists by hand?`), or go straight to the product's input: a large rounded input box, empty with placeholder text, suggestion chips underneath.
3. **Feature chapters (3–5, about 8–15 s each).** Each one is:
   - **A title line**: one short sentence, small (about 28 px at 1080p), centred. It types or fades in word by word. Then the **camera pushes in** until the line spans about 75 % of the frame width, and **one key word gets a highlight**: a soft brand-colour box sweeping left to right behind it.
   - **The UI moment**: the product's real interface rebuilt as clean vector UI (shape layers and text, not screenshots), cropped to the part that matters and shown big. The camera rides along with the action: text typing into the input (the camera follows the caret), an agent's steps ticking off one by one (spinner → check), result cards stacking up with the far ones blurred (depth of field), a table filling row by row, the cursor clicking a cell and the value revealing, a popover opening with reasoning and sources.
   - **The pull-back**: after the action, the camera eases out to show the whole screen for a beat, then glides on.
4. **Proof (optional, only real numbers).** A sentence with a number that counts up, the number highlighted, over a subtle dotted globe or grid.
5. **Integrations (optional).** `Built for your existing workflow.` in the centre while 8–12 app tiles float in from the edges at different depths: near ones larger and slightly blurred, far ones small and sharp, all drifting with parallax. Here the text scales up on its own instead of a camera push, so the tiles stay in frame.
6. **Closer.** On the brand gradient: one sentence with a rotating highlighted word cycling through the use cases (`Do all your [prospecting / research / outreach] in Product.`), then the tagline with its key phrase highlighted.
7. **End card (3 s).** Logo or name on the brand gradient, URL or call to action small below.

### Building it in After Effects

| Moment | Build it with |
|---|---|
| Scene camera (2D) | The scene's content in a precomp at full size; in the scene comp, keyframe the content layer's Scale and Position (or Anchor Point) for push/ride/pull with native eased keyframes (influence 70–85 %, 0.6–1.2 s) or the spring expression with `z ≥ 0.95`. Collapse Transformations on, so vector text stays sharp at 3× |
| Camera following the caret | The content layer's Anchor Point = the caret's position: on the text layer, `sourceRectAtTime().width` gives the line length; smooth it with the **camera follow** expression (`w 6`, no lead) |
| Title line, word by word | `textAnimatorPreset { preset: "blurIn" }` or `"typewriter"`; size it with `fitTextToBox` / `layoutTextStack`, never by guessing |
| Highlight sweep | A rounded-rectangle shape behind the key word (place it with `getLayerBounds` on the word, or a separate text layer for that word), anchor on its left edge (`setAnchorPoint { to: "left" }`), Scale X 0 → 100 with the spring expression (`w 14, z 1`), fill = accent at 15–20 % |
| Blur dissolve between scenes | The outgoing precomp: Opacity 100 → 0 and Gaussian Blur (`ADBE Gaussian Blur 2`) 0 → 30 over 0.35 s; the incoming one already moving underneath |
| Rebuilt UI | Shape layers (rounded rectangles, 1 px strokes `#E7E7EC`, white fills, soft Drop Shadow `ADBE Drop Shadow` at low opacity) and text layers; align with `alignLayers` / `distributeLayers` |
| Typing in the input | The **typing** expression (25 characters per second) |
| Steps ticking off | Per step: a spinner (shape with Trim Paths rotating) that swaps to a check (content swap expression) at the step's time |
| Cards stacking with depth of field | 3D layers at different Z, a camera with `setupDOF { focusLayerName }` |
| Table filling row by row | One precomp per row, staggered with `staggerLayers`; each "thinking" cell = a shimmer (a gradient bar sliding across, masked to the cell) before its value appears |
| Cursor | A macOS-style arrow (shape path), Position keyframes on gentle curves (spatial bezier), arriving a beat before each click; on the click a small scale dip (spring, `w 22`) and a soft ripple (ring shape scaling up and fading) on the clicked control |
| Count-up | Slider + the **count-up** expression |
| Floating integration tiles | 3D tile precomps at different Z with slow drift (`wiggle(0.3, 20)` after `seedRandom(index, true)`), far ones small and sharp, near ones larger with a little blur |
| Silk brand gradient | Fractal Noise (`ADBE Fractal Noise`) stretched wide, Evolution keyed slowly, coloured with Tint (white → pale accent → accent), heavily blurred, in its own precomp so the blur renders once |
| Rotating highlighted word | One text layer per word, swapped with the content swap expression inside a highlight box whose width springs to each word's width (`getLayerBounds`) |

### Rules that make it feel premium

- **One thing at a time.** Never more than one line of text plus one UI element on screen. Text scene, then UI scene.
- **The camera is the editor.** No hard cuts. Every scene change is a camera move or a soft blur-dissolve on the plain canvas. Camera moves are smooth eases (0.6–1.2 s) or heavily damped springs (`z` ≥ 0.95); nothing bounces.
- **Real UI, made clean.** The product's real layout, labels, colours and corner radii, simplified to what the scene needs. Believable example data. Soft shadows, 1 px borders, generous whitespace.
- **Type:** the fonts from the brief. Title lines are set small (they become big through the camera, not the font size).
- **Default palette:** canvas `#F7F7F8`, text `#111114`, secondary `#8A8A94`, UI surfaces white with `#E7E7EC` borders, accent `#2E6BFF`, highlight box = accent at 15–20 % opacity. Brand colours replace the accent.
- **Pacing:** each title line holds about 2 s after it lands; UI moments run at real speed (typing at about 25 characters per second), with 0.5 s pauses after each result.
- **Banned:** busy backgrounds behind UI, more than one accent colour, bouncy easing, emoji, big drop shadows, glassmorphism everywhere, invented metrics or testimonials.

### Sound

An uplifting, gentle bed at 100–110 BPM, quiet and warm. Small sound effects: key ticks while typing, soft clicks, a light tick per completed step, a soft whoosh on big camera moves, a gentle chime (pop or ding) on the end card. Mark each as an `sfx:` comp marker while you build (`sfx: typing | prompt typed` with duration = the typing time, `sfx: click | Run pressed`). The music sits in the background, it doesn't drive the edit.

## Step 3: Check, render, deliver

Follow `ae-motion-core`:

1. **Stills.** `render-frame` at one time per beat-sheet row (and once mid-push per chapter). Fix anything clipped, overlapping, unreadable, off-brand or badly framed. Check again.
2. **Draft.** Draft Settings to H.264; send it to the user with the script and ask for changes before the final.
3. **Final.** Best Settings, motion blur on, silent H.264. A 60 s final with depth of field and motion blur can take a while; say so before starting.
4. **Sound.** Run `ae-sound-effects` on the silent final with the music.
5. **Deliver** the saved AE project, the MP4 with sound, and a short note: the script, what is placeholder, the fonts used, and one alternative direction in a sentence.

Adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) `explainer-default` skill (MIT).
