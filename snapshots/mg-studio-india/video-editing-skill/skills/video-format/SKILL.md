---
name: video-format
description: Lays out visual scenes with HyperFrames Catalog as the first-class foundation. Replaces ad-hoc custom containers with polished registry blocks, wires layouts, and keeps compositions fully editable via CLI tools and modular sub-compositions.
---

# Format & Layout (HyperFrames Catalog-First & Composition Architecture)

> **Styles:** Layout styles #1-20 (`references/styles-layout-composition.md`) and card / list styles #111-144 (`references/styles-cards-lists.md`) of the 225-style catalog.

Never write arbitrary custom CSS boxes or amateur developer containers. **The HyperFrames Catalog (~450 production-grade blocks and components) combined with the 225-Style Taxonomy (`video-plan-storyboard/references/style-catalog.md`) forms the first-class spatial foundation for all on-screen graphics.**

Formatting is not just dumping random cards onto raw footage. It is the deliberate spatial architecture of canvas framing, background containers, typography hierarchies, safe-zone margins, and motion graphics.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Context-Driven Layout Formats & Multi-Layout Shifts

The default editing style must be **creative, innovative, and trendy** (Vox, MagnatesMedia, top-tier creator caliber). Do not lock the entire video into a static full-screen talking head. Instead, dynamically shift A-roll layouts across narrative beats:

| Layout Format | Composition Architecture | Best-Fit Content & Empty Space Role |
|---|---|---|
| **Full-Bleed Presenter** | Full camera shot with subtle cinematic grade and responsive captions. | Opening emotional hook, bold statements, punchy sign-offs. |
| **Corner Picture-in-Picture (PiP)** | Presenter video minimizes to an elegant squircle or circle in a corner (~28-34% width), clearing platform UI. | **Opens 70% of canvas** for researcher articles, 3D mockups, animated financial charts, and evidence cards. |
| **Bottom Split-Screen (70% Standard)** | Presenter occupies bottom 40-45% of canvas with top/bottom crop focusing on head area; clean 2-3px styled divider or rounded card edge. | Upper 55-60% pane dedicated to active HyperFrames motion scenes, researcher articles, or kinetic charts. |
| **Speaker Cutout / Matte on Styled Canvas** | Speaker cutout/silhouette extracted and placed over a dynamic graphical, neutral dark (#0f172a, #111116), clean white, or cinematic gradient backdrop. | Premium documentary feel: text, animated charts, and 3D icons float behind and around the speaker with physical depth. |
| **Full Graphic & Research Canvas** | A-roll momentarily hides or tucks away; full graphic canvas takes center stage. | High-impact data reveals, document leaks, animated map routes, or complex infographic comparisons. |

---

## 2. Empty Space Utilization & Canvas Elements

When the A-roll is minimized or shifted into split/PiP view, the newly opened canvas space must be actively and creatively populated:

1. **Researcher Articles & News Clippings:**
   - Real or simulated newspaper/publication articles with authentic mastheads.
   - An animated fluorescent yellow, cyan, or gold marker pen sweeps across the headline or key quote (`width: 0% -> 100%`, `duration: 0.4s`).
   - Slight 3D rotation (`rotateZ: -1.5deg`, `perspective: 1000px`) and realistic drop shadow.
2. **Kinetic Data Charts & Visualizations:**
   - Animated SVG / HTML bar charts comparing figures (e.g. BYD 40 Lakh vs Mahindra 50,000).
   - Animated line growth curves showing GDP expansion, revenue jumps, or subscriber trajectories.
   - Live counting metric pills (`+1.7%`, `27 LAKH JOBS`, `₹10,000 CR`) with spring pop entrances.
3. **3D Objects, Device Mockups & Depth Cards:**
   - Isometric cards tilted in 3D space (`transform: perspective(1000px) rotateY(-18deg) rotateX(8deg)`).
   - Floating smartphone or laptop frames displaying tweets, web pages, or social media handles.
   - Layered depth with blurred ambient glows and directional lighting.
4. **Natural Physics in Motion Graphics:**
   - Elements enter with momentum and settle with damped harmonic springs (`power3.out`, `back.out(1.4)`).
   - Zero rigid or cartoonish linear motion.

---

## 3. Dynamic Headroom & Spatial Guardrails

1. **Strict Clean Headroom Rule:**
   - **Never** place headline bars, floating checklist pills, or topic badges directly over the creator's forehead, hair, or ceiling space.
   - Plastering checklist cards in the top air (as seen in awkward amateur videos) creates visual claustrophobia.
2. **Dedicated Graphic Zones:**
   - On-screen cards, list items, specs, and badges are placed dynamically in the lower visual region, side rails, or dedicated full cutaways.
3. **Proportional Platform Safe Margins (Resolution-Agnostic):**
   - Safe margins scale proportionally with probed canvas dimensions (`W` x `H`):
     - **Top Margin (~9.4% of H):** Clears platform search, sound bar, and camera cutout.
     - **Bottom Margin (~16.5% of H):** Reserved for platform interaction bar, description drawer, and captions.
     - **Side Margin (~7.5% of W):** Safe distance from right-hand engagement buttons (like, comment, bookmark, share).
   - This ensures safe zones remain mathematically exact whether editing 4K (`2160x3840`), Full HD (`1080x1920`), horizontal, or square videos.

---

## 4. Catalog-First Execution Protocol (Pre-Installed Offline Library)

All 447 compositions and components from the HyperFrames registry are pre-installed into the global engine cache (`$ENGINE_DIR/compositions/`) during installation (`install.sh`). There are zero cold network fetches required during an edit.

1. **Pre-Cached Local Inventory:**
   Look up verified components instantly from `references/index.json` or query the local library directly:
   ```bash
   ls "$ENG/compositions"
   ```
2. **Instant Staging from Local Cache:**
   When a blueprint preset is selected (e.g. `B19` or `B33`), `parallel_pipeline.py` automatically stages its linked compositions from the global cache into `$W/hyperframes/compositions/`.
3. **Adaptive Customization (Similar Effects vs Blind Copying):**
   The editor tailors the staged HTML/CSS/GSAP composition across 5 dimensions:
   - **Content Injection:** Replace stock placeholder text/stats with the speaker's exact spoken numbers and claims.
   - **Color & Brand Tokens:** Apply the active color scheme (`#ffe600` accent, `#1e293b` studio backdrop).
   - **Beat Synchronization:** Align entrance animations (`data-start`, `tl.fromTo`) with transcript phrase timestamps.
   - **Spatial Clearance:** Scale and anchor the component safely within chin-safe coordinates.
   - **Animation Dynamics:** Retain critically damped harmonic motion (`power3.out`, `back.out(1.3)`).
4. **Wire into Storyboard:**
   Mount as a modular sub-composition (`block` / `<div data-composition-src="...">`) or component snippet inside `$W/hyperframes/index.html`.

---

## 5. Catalog Mapping by Use Case

| Visual Intent | HyperFrames Catalog Query | Verified Catalog Components |
|---|---|---|
| **Researcher Articles & News** | `query "newspaper article headline clip"` | `article-highlight-zoom`, `newspaper-headline-rip`, `tweet-card-pop`, `browser-mockup-scroll` |
| **Kinetic Data Charts & Stats** | `query "bar chart animated stat counter"` | `bar-chart-animated`, `growth-curve-draw`, `stat-callout-counter`, `counter-flip` |
| **3D & Isometric Depth Cards** | `query "isometric 3d card tilt mockup"` | `isometric-card-3d`, `floating-mockup-tilt`, `coin-spin-3d`, `split-tilt-cards` |
| **Split-Screen & Comparison** | `query "split screen comparison"` | `comparison-split`, `before-after-wipe`, `split-tilt-cards` |
| **Clean Lower Third & Header** | `query "lower third headline banner"` | `lt-minimal-glow`, `lt-headline-banner`, `headline-ticker` |
| **Product / Feature Specs Card** | `query "product card feature showcase"` | `mk-specs-list`, `feature-pill-card`, `grid-card-assemble` |
| **Optical Transition & Light Leak**| `query "flash transition light leak"` | `flash-through-white`, `transitions-light`, `editorial-flash-overlay` |
| **Paper / Texture Accents** | `query "paper rip collage texture"` | `torn-paper-rip`, `paper-collage-reveal`, `marker-checklist-card` |

---

## 5. CLI Composability & Composition Hygiene

To guarantee that the video is seamlessly composable and verifiable via CLI tools:
- **Modular Sub-compositions:** Place distinct visual treatments in `$W/hyperframes/compositions/<name>.html` rather than pasting hundreds of messy DOM nodes into one giant monolithic file.
- **Semantic Track Structure:** Use clean track indexing (`data-track-index`):
  - Track 1: Base creator video.
  - Track 10-20: Transitions & flashes.
  - Track 30-40: Catalog overlays, cards, and banners.
  - Track 50-60: Natural flowing captions rail.
  - Track 70+: SFX audio cues.
- **Relative Coordinates & Variables:** Use semantic CSS variables for fonts, primary colors, and accent colors defined in `style.json`.
- **Validation:** Always verify with `npx hyperframes lint "$W/hyperframes"` and `npx hyperframes check "$W/hyperframes"` before user handover.
