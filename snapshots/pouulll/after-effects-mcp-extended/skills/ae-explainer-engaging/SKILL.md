---
name: ae-explainer-engaging
description: Make a 10–30 second continuous-shot explainer for any product in Adobe After Effects through the After Effects MCP server. One hero element (a ball, a cursor, a file, a message) travels through the product's workflow laid out as stations on one big canvas, with real hop physics, squash and stretch and a following camera; each station reacts as it passes, then the camera pulls out to reveal the whole journey. Rendered with aerender and given a measured sound pass. Use when someone wants an engaging, story-driven, one-take explainer or a loopable product animation built in After Effects.
---

# Engaging explainer (After Effects)

A one-take visual story. A single **hero element** (in the reference style, a white ball that starts as a toggle's knob) travels through a chain of small interface "stations", and each station reacts to it: it rolls along a slider and pushes it to 100, falls off the end and bounces down a stack of notifications that pop up as it passes, lands on a keyboard and bounces key to key typing a word, hits return and is launched back into the air. The camera **never cuts**: it keeps the hero near the centre and zooms in for each interaction, and at the climax it pulls far out so the viewer sees the whole course at once, before diving back to where it all started.

For a product, the stations are the **steps of its workflow**, laid out spatially on one canvas, and the hero is the thing that moves through it. The pull-out is the "now you get how it works" moment.

You build it as an After Effects project with the MCP tools, render it with aerender and add sound with `ae-sound-effects`. **Load `ae-motion-core` first.** This skill leans on its tested expressions: ballistic hops, squash and stretch, camera follow and the apex time warp.

## Step 1: Get the brief (one message, then go)

Ask everything in **one** message, then work on your own. Only the product and the fonts are required; for anything else left blank, decide yourself and say what you chose.

1. **Product**: name, and what it does in a few sentences. A website URL is even better.
2. **The one thing** the viewer must remember.
3. **Brand**: colours, logo file, or "use the website". If none, use the default palette below.
4. **Fonts**: which typefaces to use, and for what (station labels, card titles and body, the typed input; usually one family, optionally a code font for the input). Offer 4–8 options from the fonts installed on this machine (see `ae-motion-core`, step 3) plus any brand fonts named on their website that are installed. This is the user's call: never pick a font for them, and don't start building text until they have chosen.
5. **Format**: 16:9 (1920×1080) or 9:16 (1080×1920). Default 16:9.
6. **Length**: default 12 s, seamless loop. Range 10–30 (longer = more stations, not slower stations).
7. **Music**: their own track, or a free track from the sound-effects skill's `MUSIC.md`. Never synthesise music.
8. **Workflow** (optional): 3–6 steps (what the user does → what the product does → the result). With a URL, derive it from the site.
9. **Direction** (optional): anything they want or want to avoid.

If they gave a URL, read it for the product's real wording, features and colours (and font names, only to offer them as options). **Never invent facts**: example content inside the UI is fine, claims about the product (stats, ratings, offers) are not. Logos only if supplied; otherwise the name as text.

## Step 2: Design the course, then build

### 1. Choose the hero

One simple, readable object the story is about. It never disappears or gets replaced (it may change shape for a moment, then return): a ball/knob (default, works for anything), a caret or cursor, a file tile, a message bubble, a coin, a data point. It should fit a station naturally (a knob, a thumb, a key cap, a pin).

### 2. Map the workflow onto stations

Each step becomes one station: a compact real interface element that the hero physically interacts with and that **visibly changes because of it**.

| Mechanic | The hero... | The station reacts |
|---|---|---|
| Toggle / button | is the knob, or presses it | switches on, colour fills |
| Slider / progress | rolls along it as the thumb | value counts up in a tooltip, track fills |
| Notification stack | falls and bounces on each card | each card pops in as it is hit, its message narrating the story |
| Keyboard / input | bounces key to key | each key presses down, letters appear in the input above |
| List / table | slides down the rows | each row highlights, ticks or sorts |
| Chart | becomes the line's leading dot | the line draws behind it, bars rise as it passes |
| Chat | rides in as a bubble | the reply types out |
| Deploy / send button | is launched by it | a toast or URL appears |

Station labels and messages tell the story in a few words each, with some wit (`Slider · Reached 100`, `Gravity · Something is falling`, `Messages · What now?`). For a product, write them from its real workflow.

### 3. Lay out the world

Build every station inside one **World** precomp about 3× the frame (5760×3240 for 16:9), in visiting order, so the path zig-zags (right along the top, down through the middle, across the bottom). Falls go down, launches go up. Each station's spot is fixed for the whole video. The world is a dark canvas with a faint dot grid (Grid effect or a Repeater shape) that moves with the camera: the grid is what makes camera moves readable.

### 4. Script the hero's path

Settle the music and measure its tempo **before** writing the beat sheet (`ae-motion-core`, "Music first"): the contacts are the rhythm, so the grid must be the track's.

The hero is a shape layer inside World, anchor point on its **bottom centre**. Its path is Position keyframes, one per **contact**, each on a beat (`bpmMarkers` gives you the grid):

- **Hops and falls**: the **ballistic hops** expression on Position. x moves linearly, y falls under one gravity (`g` constant for the whole video) and lands on the next contact exactly at its time. Check every contact with `sampleProperty`: value and time must match the key.
- **Rolling/sliding** along a station: put a layer marker with the comment `slide` on the contact where the slide starts; that segment eases instead of hopping. Derive the station's value from the hero's position (e.g. the slider's fill width = `hero.x − track.left`).
- **Impacts**: the **squash and stretch** expression on Scale (1.25 × 0.8 on contact, stretch in flight). Whatever was hit gets a small push-down: 6–10 px down and back with the spring expression.
- **The launch**: the last station fires the hero up and back toward the start in one long arc, while every station **resets in reverse** behind it (values count down, notifications dismiss, the input clears) so the loop closes. Slow it with a `slowmo <T>` marker on the launch key (the hop expression plays a real `T`-second flight over the whole segment, slowest at the apex, often 5–10×). Choose the apex height first (the top of the course); schedule the station resets during the reveal hold, after the viewer has seen the full course.
- **Seam**: put the loop point at the hero's landing on the first station. The landing squash and key press also show at time 0. Set `loop = true` in the camera follow, and run the seam check from the expression library.
- **Keep the hero's paths clear**: no labels or UI directly above a take-off or along an arc, or the hero flies through them (check the contact sheet).
- **Gravity is side-on.** Notification cards form a staircase (each offset sideways by more than its width, so the hero never passes through one); the keyboard is seen head-on with the hero hopping between keys in small arcs.
- **The empty slot**: when the hero was part of a station (a knob, a thumb) and leaves, the station keeps a dim outline of the slot, which fills again when the hero returns.

### 5. The camera

The camera is the hard part; get it right before polishing anything else.

- **Rig**: put the World precomp in the main comp. A null `CAM TARGET` *inside* World carries the **camera follow** expression (target = the hero, `w` ≈ 6, lead 0.15 s) with the anchor blend: a Point Control `Anchor` per station (hold keys) and a Slider `Anchor weight` (0.7 during an interaction, 0.15 in falls and hops, 0.85 on the payoff hold). In the main comp, the World layer's **Anchor Point** = `comp("World").layer("CAM TARGET").transform.position`, its Position = frame centre, its **Scale** = zoom. Collapse Transformations on.
- **Start**: at time 0 the weight is 1 on the first station's anchor and blends to following over the first 0.8 s (keyframe the weight).
- **Zoom** (World Scale, spring-between-keyframes, `z` 1): tight during each interaction (the station fills about half the frame width, the hero 50–70 px on screen at 1080p); slightly wider during falls and hops so the next station is already visible. The hero never leaves the middle half of the frame: check with `getLayerBounds` on the hero at the contacts.
- **Payoff hold**: before the launch, hold on the final result for 0.4–0.6 s, fully in frame.
- **The reveal**: on the launch, the camera stops following (weight → 1 on a fixed whole-course anchor) and zooms out to fit the whole course (about 0.3×), with a slight 3D tilt (make World a 3D layer and key X Rotation 15–25°, with a camera). Hold about 1 s while the hero arcs across; scale the hero up and give it a soft glow (`ADBE Glo2`) so it stays the brightest thing (at least 24 px on screen). Then **dive** back to the first station's framing, timed so the hero lands as the camera arrives, and blend back into following.
- **Motion blur on**: the hero and the world smear on fast moves; that is part of the look.

### Look

- **Default palette** (dark iOS-like): canvas `#0C0C0E`, dot grid `#1E1E22`, surfaces `#1C1C1F` / `#2C2C2E`, text `#F2F2F7`, secondary `#8E8E93`, accent `#0A84FF`, hero white `#FFFFFF`. Brand colours replace the accent; the hero stays the brightest thing on screen. A light variant (canvas `#F2F2F4`, hero = accent) is fine for a light brand.
- Real-looking system UI built from shape layers and text: toggles, sliders with tick marks, notification cards (app icon square, title, body line, `now`), a keyboard with key caps and a return key, in the fonts from the brief.
- A cursor may start the chain (clicks the first station) and then gets out of the way.
- **Banned:** cuts, fades to black, text overlays explaining what is happening (the stations' own labels are the only text), more than one hero, stations that don't react, physics that look floaty (raise `g` if hops feel slow).

### Sound

A tight, minimal groove at 110–120 BPM, and the **hero's contacts are the main instrument**: each impact a short tick or pop, key presses click, notifications a soft pop, the launch a whoosh up and the dive a whoosh down. Every contact already has a time (its Position keyframe): add a comp marker for each (`sfx: pop | hits card 2`, `sfx: click | key R`, `sfx: whoosh | launch`) so the sound pass lands each sound exactly on its contact.

## Step 3: Check, render, deliver

Follow `ae-motion-core`:

1. **Numbers first.** `sampleProperty` the hero at every contact (lands exactly), the squash at contacts (1.25 × 0.8), and the camera target (no jumps).
2. **Stills.** `render-frame` at each contact, mid-hop, the payoff hold, the reveal and the seam. Fix framing, overlaps, unreadable labels.
3. **Contact sheet.** `renderFrames` every 2–3 frames through one bounce and one camera move; check arcs and spacing.
4. **Draft** (Draft Settings, H.264) to the user; changes; then the **final** (Best Settings, motion blur on, silent), then **sound** with `ae-sound-effects`.
5. **Deliver** the saved AE project, the MP4 with sound, and a short note: the course (stations in order), what is placeholder, and one alternative direction.

Adapted from Bart's [motion-graphics](https://github.com/Barty-Bart/motion-graphics) `explainer-engaging` skill (MIT).
