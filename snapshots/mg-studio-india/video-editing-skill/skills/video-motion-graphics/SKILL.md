---
name: video-motion-graphics
description: Builds animated elements and tunes physical motion dynamics (springs, inertia, kinetic typography, scale pops, camera punch-ins) as seek-safe HyperFrames compositions.
---

# Motion Graphics & Dynamics (HyperFrames Catalog & Physical Kinetics)

> **Styles:** Animation, transition & VFX styles #76-110 of the 225-style catalog: `references/styles-animation-transitions-vfx.md`.

Animations and motion graphics in professional video must obey physical laws: inertia, mass, damping, and momentum. **Static scenes without motion graphics feel dull, while cheap or floaty linear animations ruin perceived production value.**

This skill bridges the 450+ component **HyperFrames Catalog** with custom seek-safe GSAP motion design to create animated counters, lower thirds, progress indicators, product cards, and optical transitions.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Visual Elements Catalog & Presets

Always query the HyperFrames catalog first (`npx hyperframes catalog --query "<intent>"`) before writing custom graphics.

| Motion Graphic Element | HyperFrames / GSAP Implementation | Physical Kinetics & Role |
|---|---|---|
| **Kinetic Data Charts & Graphs** | `bar-chart-animated`, `growth-curve-draw`, `stat-comparison-meter` | Bars scale upward (`scaleY: 0 -> 1`, `transform-origin: bottom`) with snappy momentum; comparison growth curves draw dynamically with SVG path length animation. |
| **Researcher Article & Media Clippings** | `article-highlight-zoom`, `newspaper-headline-rip`, `tweet-card-pop` | Realistic newspaper/journal mastheads entering with subtle 3D tilt (`rotateZ: -1.5deg`); animated fluorescent yellow/cyan highlighter pen sweeps across the key quote (`width: 0% -> 100%`, 0.4s). |
| **3D Isometric Depth Cards & Mockups** | `isometric-card-3d`, `floating-mockup-tilt`, `coin-spin-3d` | Floating 3D perspective (`transform: perspective(1000px) rotateY(-18deg) rotateX(8deg)`), ambient drop shadow, natural spring settle on entry. |
| **Stat Counter & Metric Badge** | `stat-callout-counter`, `badge-pill-pill` | Counts up with ease `power2.out`, spring pop entrance on number claim (`+1.7%`, `27 LAKH`, `₹10,000 CR`). |
| **Clean Lower Third & Topic Pill** | `lt-minimal-glow`, `lt-headline-banner` | Smooth 0.24s slide-in from left with 4px settle; anchors topic without covering face. |
| **Specs & Feature Cards** | `mk-specs-list`, `feature-pill-card` | Staggered cascade (80ms delay) from lower third (`y: 35px -> 0px`). |
| **Progress Indicator Bar** | Top or bottom thin progress line (2px) | Steady seek-safe timeline scrub tracking reel duration. |
| **Optical Transition Flashes** | `flash-through-white`, `transitions-light` | 2-frame white peak with 0.18s decay on scene or topic shifts. |
| **Icon / Logo Pop** | Scaled SVG vector mark with glow border | `scale: 0.85 -> 1.08 -> 1.00`, `-2deg` micro-rotation on entry. |

---

## 2. Physical Motion Standards

Every animated element must adhere to these kinetic principles:

### A. Damped Harmonic Motion (Spring Physics)
- Text and cards do not stop abruptly with linear easing or bounce like cartoon rubber balls.
- Use **critically damped harmonic motion**:
  - `stiffness`: `160 - 200`
  - `damping`: `14 - 18`
  - `mass`: `1.0`
- In GSAP terms: `power3.out` for snappy entrances, `back.out(1.3 - 1.4)` for subtle physical overshoot (5-8% maximum), and `power2.in` for clean exits.

### B. Micro-Scale Pop Dynamics
- Keyword punch cards and caption badges enter with an explosive scale pop that settles naturally:
  - Frame 0: `scale: 0.88`, `opacity: 0`
  - Frame +6 (0.10s): `scale: 1.06`, `opacity: 1`
  - Frame +12 (0.20s): `scale: 1.00`
- Simulates physical mass decelerating into place.

### C. Directional Momentum & Tilt Physics
- When elements slide in from the bottom or side, add subtle rotational momentum:
  - Moving upwards: starts with `rotation: -2.0deg` and `y: 35px`, settling to `rotation: 0deg` and `y: 0px`.
  - Breaks rigid digital alignment and feels like a physical sticker or card landing on glass.

### D. Multi-Element Stagger Physics
- When multiple items enter (e.g. 3 product cards, bullet points, feature specs):
  - Stagger timing must be **60ms - 90ms** (`stagger: 0.08s`).
  - Slower staggers (>150ms) feel sluggish; faster staggers (<40ms) blur together visually.

### E. Camera Punch-In Kinetics
- Camera scale zooms (e.g. `1.08x` or `1.12x`) must snap instantaneously on the acoustic onset of the emphasized word (within 0.08s - 0.12s), settling with zero float.
- Avoid slow, floaty zooms during fast-paced reels; punch-ins must feel like a hard lens switch or snap zoom.

---

## 3. Seek-Safety & Deterministic Rendering

Because HyperFrames renders on headless Chromium frame-by-frame:
1. **Never use non-deterministic properties:** No `Math.random()`, no unseeded particle generators, no `setTimeout` or `setInterval`.
2. **Timeline Control:** Every animation must live on a paused GSAP timeline tied to the master composition clock (`data-start` and `data-duration`).
3. **Hardware Acceleration:** Animate transform properties (`transform: translate3d(x, y, 0) scale(s) rotate(r)`) and `opacity` only; never animate layout reflow properties (`width`, `height`, `top`, `left`, `margin`).

---

## 4. Multi-Layout Motion Scenes (Split & PiP)

- **Active Canvas Integration:** In split-screen (top 44% speaker) and corner PiP formats, the opened canvas is never left bare or black. It is populated with active HyperFrames motion scenes tailored to the speaker's words.
- **Composition Staging:** Verified HyperFrames blocks and components (e.g. `chart-story`, `comparison-split`, `marker-checklist-card`, `x-post`) are staged into `hyperframes/compositions/` and animated deterministically via GSAP to sync with speech beats.
