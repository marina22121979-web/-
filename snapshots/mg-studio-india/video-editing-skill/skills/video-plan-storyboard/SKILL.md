---
name: video-plan-storyboard
description: Plans the narrative, creative hook, visual storyboard, video effects, motion dynamics/physics, typography, and color grading BEFORE making cuts or assembling the video. Owns Gate 3.
---

# Plan & Storyboard (Pre-Cut Creative & Physics Architecture)

> **Styles:** Style catalog (all 225 styles, schema, owning file per style): `references/style-catalog.md` · storytelling styles #145-172 `references/styles-storytelling.md` · commercial & platform styles #201-225 `references/styles-commercial-platform.md` · duration & delivery `references/duration-delivery.md`.

Professional videos succeed or fail in the storyboard. **Storyboarding must happen BEFORE cutting raw footage or generating edits.** Cutting without a storyboard results in disjointed, mechanical clips that lack retention, context, and emotional pull.

**Mandatory Visual Storyboard & Rendered Mockups Requirement:**
Never present an abstract text-only plan. Every storyboard must be generated and saved to `$W/STORYBOARD.md` embedded with:
1. **Rendered Keyframe Screenshots:** Real video frames extracted at each narrative beat transition showing framing, safe zones, and speaker clearance.
2. **Dynamic Frame-Accurate Color Correction Sheet:** A side-by-side comparison sheet (`preview/grade-preview.jpg`) dynamically calculated from actual frame pixel distributions (shadow floor $P_1$, specular ceiling $P_{99}$, midtone gamma $P_{50}$, adaptive contrast, natural vibrance, and 5650K daylight calibration) so the user can verify skin tones and look before cutting. Zero artificial static filter presets.
3. **Tight Cut Plan:** Duration metrics comparing raw footage vs tight cut, highlighting trimmed dead air.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Grounding in Gate 1 Specifications (`resolved-spec.json`)

The storyboard generator directly ingests `$W/resolved-spec.json` (resolved in Gate 1) across the 6 core pillars:
- **Format & Multi-Layout:** Context-derived format (Choreographed multi-dynamic, 40/60 Split View, Screen-plus-Facecam, Corner PiP, Speaker Cutout)
- **Sounds & Music Bed:** Tactile whooshes, paper tears, clicks, ducked lofi or synth bed
- **Caption Styling:** Single-row vibrant captions (`0.048 * W`, 1-4 words max, `#ffffff` white, `#ffe600` active word, `#00f59b` punch word)
- **Dynamic Color Correction:** Statistically calculated directly from frame pixel distributions (shadow floor, specular ceiling, midtone gamma, adaptive contrast, natural vibrance, daylight calibration). Zero static filter presets.
- **Motion Graphics:** Active HyperFrames motion scenes, researcher articles, kinetic data charts, 3D depth cards
- **Audio Processing:** 80Hz rumble cut, EBU R128 loudness normalization, whisper.cpp ASR with Hinglish transliteration

Every beat in `storyboard.plan.json` must be grounded in these resolved choices.

### User Direction Protocol (Gate Q before Storyboard):
If the user did not explicitly specify their editing preferences (e.g. preset choice, layout mode, proof requirements) in their initial prompt, the agent invokes `ask_question` **before running `video-plan-storyboard`**. The user chooses:
- Preferred proven video-preset (ranked by `video-reference-match` from the transcript)
- Layout choreography (Split-Screen, Floating Squircle PiP, Full-Frame with punch-ins)
- Evidence & proof elements to highlight
This choice directly dictates how the storyboard and motion scenes are structured.

### Collaborative Storyboard Pillars:

1. **Creative, Innovative & Trendy Multi-Layout Architecture:**
   - **Never default to a static full-screen talking head.** Actively choreograph A-roll layout transitions across narrative beats:
     - *Hook:* Full camera shot with snap punch-in (1.10x) for personal impact.
     - *Proof & Comparison Beats:* A-roll minimizes into a floating corner PiP squircle/circle, or shifts into a split view where the speaker takes the bottom pane (70% standard) with top/bottom crop focusing on head area visibility, opening the upper canvas for active HyperFrames motion scenes, research articles, and animated data charts.
     - *Core Breakdown Beats:* Speaker cutout/matte or framed card on a modern graphical, neutral dark (#0f172a, #111116), clean white, or cinematic gradient canvas.
   - **Empty Space Utilization:** Every non-full-frame beat MUST specify the visual asset occupying the opened space:
     - *Researcher Articles:* News headlines, financial journal tear-outs, and tweets with animated highlighter sweeps.
     - *Kinetic Data Charts:* Animated bar graphs, percentage growth curves, and live metric counters.
     - *3D Objects & Mockups:* Isometric depth cards, floating phone mockups, and product visuals.
2. **Visual Direction & Overlay Rules (No Cluttered Forehead Overlays):**
   - **Strict Rule:** Never place persistent top headline bands or floating checklist card pills over the creator's forehead or hairline. Floating boxes pinned to the ceiling look amateur and awkward.
   - Overlays (cards, lower thirds, callouts) must be contextual and positioned in lower safe zones (`y: 0.58 - 0.75`), side panels, or dedicated cutaways.
3. **Cuts & Pacing:**
   - Discuss cut rhythm (fast retention cuts 1.2-1.8s vs relaxed conversational pauses 2.5-4.0s).
   - Identify retakes, stumbles, and tangent lines to cut or keep.
4. **Effects & Optical Transitions:**
   - Agree on transition styles: hard cuts, light leaks, white flashes, film grain, or camera punches.
5. **References & Inspirations (References Take Precedence):**
   - **References Precedence:** User-supplied references in `references/` or `videos/<project>/references/` always take absolute precedence over catalog blueprints. Incorporate the reference reel's measured pacing, framing, and visual devices first; catalog blueprints supply the matching HyperFrames compositions to execute that aesthetic.
   - If Gate R chose a style blueprint, build the storyboard from `$W/reference-match/ROADMAP.md` (`video-reference-match`): its structure, pacing, elements and catalog style IDs, with the brand tokens filled; the grade still comes from this footage.
6. **Input Folder Inventory & Strict Raw Ingestion:**
   - **Audit the raw input folder:** Inspect `videos/<project>/raw/` and list every provided file (face camera, screen recordings, b-roll, audio, photos).
   - **Strict Adherence Boundary:** All user raw inputs must be sourced exclusively from `videos/<project>/raw/`. If the user mentions other folders or external files, only assets located within `raw/` are ingested and processed. External mentions are treated as advisory context only.
   - **Suggest recording more content:** If the speaker mentions a product, screen demo, website, or action that lacks footage, actively suggest:
     > *"You discuss [X] at [timestamp]. We don't have b-roll for it in the raw input folder. Would you like to record a quick 5-10 second b-roll / screen capture of [X] and drop it into raw/? It will make this moment significantly more compelling! Otherwise, we can design an animated graphic card or generate an image."*
7. **Generative Assets vs HyperFrames Animations:**
   - Discuss whether AI stills (Gemini Flash), AI video inserts (Veo), or HyperFrames/Remotion programmatic animations are needed.
8. **Dynamic Color Correction & Frame Comparison Sheet:**
   - Execute `grade.py` to statistically calculate dynamic parameters ($P_1$ black floor, $P_{99}$ specular ceiling, $P_{50}$ midtone gamma, adaptive contrast, saturation, and 5650K daylight calibration).
   - Generate `preview/grade-preview.jpg` comparing raw frames vs dynamically graded frames for the user to review. Zero static filter presets.
9. **Autonomous Caption Styling (Zero User Burden):**
   - The user does not need to configure complex caption styles. The pipeline autonomously enforces small, vibrant, single-row captions (1-4 words max, `#ffffff` with `#ffe600` active word and `#00f59b` punch word) positioned safely below the speaker's chin.

---

## 2. Complete Storyboard Matrix (Per-Beat Specification)

Every beat in `plan.md` and `storyboard.plan.json` must define 5 architectural pillars:

### A. Video Effects (VFX) & Transitions
Specify the optical treatment for transitions and overlays:
- **Optical Flashes:** `flash-through-white` (hold 2 frames, decay 0.18s), `light-leak-warm`, `lens-flare-anamorphic`.
- **Atmospheric FX:** Film grain overlay (8-12% opacity, fine 35mm), vignette edge falloff (15-20% black curve).
- **Surface & Texture:** Glassmorphism frosted backdrops (`backdrop-filter: blur(16px)`, border: 1.5px solid rgba(255,255,255,0.15)), paper tear edges, glow drop-shadows.

### B. Dynamic Color Correction & Tone Balance
Ground the lighting and color balance directly in the frame pixels:
- **Dynamic Calculation:** Statistically derived from frame histogram ($P_1$ black point, $P_{99}$ white point, $P_{50}$ midtone normalization).
- **Tone & Balance:** Daylight white-balance calibration (5650K neutral grey), adaptive contrast tuned to scene lighting, and healthy natural skin vibrance. Zero static color LUTs or artificial filters.

### C. Exact Typography & Font Hierarchy
No generic fonts. Explicitly specify font families, weights, sizing, and stroke parameters:
- **Punch Font (Power Keywords):** `Poppins Black (900)` or `Anton Display`, All-Caps, size 72-84px, letter-spacing -0.02em, text-stroke: 3px rgba(0,0,0,0.92).
- **Display Accent Font (Curiosity/Elegance):** `Syne Bold (800)` or `Playfair Bold Italic (700)`.
- **Supporting / Body Font:** `Inter Bold (700)` or `Poppins Medium (500)`, size 48-56px.
- **Micro / Subtext:** Size 32-38px, uppercase, letter-spacing +0.05em, opacity 0.85.

### D. Kinetics, Dynamics & Motion Physics
Specify exact movement curves, physics parameters, and timing behaviors:
- **Physics Engine Standard:** Damped harmonic motion (`damping: 14 - 18`, `stiffness: 160 - 200`, `mass: 1.0`).
- **Easing Curve:** `power3.out` for snappy entrances, `back.out(1.3)` for subtle scale-overshoot, `power2.in` for fast exits. Never use cartoonish high-bounce curves.
- **Scale Dynamics:** Micro scale pop (`scale: 0.90` -> `1.06` -> `1.00` in 0.18s) with physical momentum.
- **Tilt Physics:** Micro-rotation (`-2.0deg` to `+2.0deg`) on entrance settling to `0deg`.
- **Stagger Physics:** Multi-item cards enter with an 80ms cascade delay (`stagger: 0.08s`), moving upward with decelerating inertia (`y: 35px` -> `0px`).
- **Camera Punch Dynamics:** 1.08x - 1.12x scale zoom snapped in 0.12s on key trigger syllables.

### E. HyperFrames Catalog Foundation
- Query and install verified blocks: `npx hyperframes catalog --query "<treatment>"` and `npx hyperframes add <component>`.

---

## 3. Storyboard Spec Schema (`storyboard.plan.json`)

```json
{
  "id": "reel-plan",
  "program": "short",
  "target_duration": 38.5,
  "style": {
    "color_grade": {
      "preset": "commercial-clean",
      "contrast": 1.12,
      "saturation": 1.12,
      "color_temperature": "6200K",
      "skin_tone_protection": true
    },
    "typography": {
      "primary_punch": "Poppins-Black (900)",
      "accent_display": "Syne-ExtraBold (800)",
      "body_text": "Poppins-Bold (700)",
      "stroke": "3px rgba(0,0,0,0.92)"
    },
    "motion_physics": {
      "entrance_ease": "power3.out",
      "pop_curve": "back.out(1.3)",
      "damping": 16,
      "stiffness": 180,
      "tilt_degrees": -1.5
    }
  },
  "beats": [
    {
      "id": "beat-01-hook",
      "time_range": "0.0s - 3.2s",
      "anchor": "first key claim",
      "visual_action": "Creator makes bold statement to camera; snap punch-in 1.10x",
      "vfx": "transitions-light flash into scene; subtle 8% 35mm grain",
      "catalog_block": "lt-minimal-glow",
      "typography": "Poppins-Black 900 · 76px · #ffffff with #ffd700 punch words",
      "physics": "Fade and settle y: 20px -> 0px, power3.out, 0.24s duration",
      "sfx": "whoosh-fast"
    },
    {
      "id": "beat-02-cards",
      "time_range": "19.1s - 25.1s",
      "anchor": "three steps",
      "visual_action": "Creator explains core breakdown; lower-third card reveals",
      "vfx": "frosted glass backdrop; 1.5px subtle border",
      "catalog_block": "mk-specs-list",
      "y": 0.62,
      "typography": "Header: Syne-ExtraBold 40px #ffd700; Items: Poppins-Bold 48px #ffffff",
      "physics": "Card stagger 0.08s, spring slide-up from y: 35px, back.out(1.3), settling in 0.32s",
      "sfx": "card-pop"
    }
  ]
}
```

---

## 4. Gate 1: Interactive Storyboard & Technical Approval

Generate `plan.md` containing the complete narrative, visual matrix, typography pairings, color grading profile, and physics dynamics.

Present to the user:
1. **Narrative & Hook Strategy**
2. **Visual & Layout Breakdown (VFX, transitions, catalog blocks, clean headroom)**
3. **Typography & Font Choice (Fonts, weights, sizing, letter-spacing)**
4. **Color Grading & Mood (Selected grade.py preset, contrast, palette)**
5. **Kinetics & Physics (Scale pops, spring curves, camera punch-ins)**
6. **Asset Checklist (Confirmed b-roll, generated assets, or user-recorded additions)**

**Review document:** generate `STORYBOARD.md` (time / beat / what is on screen) from the same `storyboard.json` the
composition is built from, so the document can never drift from the edit:
`"$PY" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-plan-storyboard/scripts/storyboard-md.py" --title "<title>" --note "<what changed>" --project "$W:<id>:<label>" --out "$W/STORYBOARD.md"`.
Regenerate it after every storyboard change and ship it with the delivery.

> **User Prompt Rule:** Ask for feedback and approval. Never cut the raw video or build components until the user approves or refines the storyboard.
