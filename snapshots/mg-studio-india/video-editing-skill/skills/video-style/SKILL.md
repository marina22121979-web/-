---
name: video-style
description: Curates the visual identity (color palette, typography pairings, card themes, color grading profiles, motion physics, and business creator reel styles) as style.json. Enables interactive user verification before visual elements are built. Owns Gate 3.
---

# Style & Visual Identity (Color Grading, Typography, Layout & Physics)

Visual consistency and polished styling separate professional content from messy amateur video. **The styling, formatting, typography, color grading profiles, and physical motion kinetics must be explicitly verified with the user before building on-screen elements.**

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
W="videos/<project>"
```

---

## 1. Unified Style Architecture (`style.json`)

> [!IMPORTANT]
> **Brand Memory Integration (`brand/MEMO.md`):**
> Before generating `style.json`, always inspect `brand/MEMO.md` (or `$PROJECT/brand/MEMO.md`) and corporate style guides in `brand/` (e.g. `brand/brand-style-guide.pdf`). If present, its colors, typography, handles, logo assets, layout preferences, and thinking process must seed `style.json`. User brand memory strictly overrides generic defaults.

A production-grade `style.json` governs five interdependent visual pillars:

```json
{
  "theme": "high-ctr-creator",
  "format_layout": "clean-authority-framed",
  "palette": {
    "background": "#100e0d",
    "surface_glass": "rgba(16, 14, 12, 0.82)",
    "text_primary": "#ffffff",
    "text_secondary": "#cccccc",
    "accent_punch": "#ffd700",
    "accent_secondary": "#ff4d4d",
    "border_subtle": "rgba(255, 215, 0, 0.35)"
  },
  "typography": {
    "font_family_catalog": ["DM Sans", "Inter", "Poppins", "Google Sans", "Roboto"],
    "primary_punch": {
      "family": "Poppins",
      "weight": 900,
      "style": "normal",
      "letter_spacing": "-0.02em",
      "color": "#ffd700",
      "pill_background": "#ffd700",
      "pill_text_color": "#000000",
      "shadow": "none"
    },
    "card_header": {
      "family": "Inter",
      "weight": 700,
      "color": "#ffffff",
      "letter_spacing": "-0.01em"
    },
    "body_support": {
      "family": "DM Sans",
      "weight": 500,
      "color": "#f8fafc",
      "line_height": 1.25
    },
    "caption_inactive": {
      "family": "Inter",
      "weight": 400,
      "color": "rgba(255, 255, 255, 0.70)"
    }
  },
  "color_grade": "dynamic",
  "dynamic_color_params": {
    "imin": 0.04,
    "imax": 0.93,
    "gamma": 1.05,
    "contrast": 1.02,
    "saturation": 1.05,
    "temperature": 5650,
    "sharpness": 0.12
  },
  "captions": {
    "mode": "phrase",
    "case": "as_spoken",
    "inactive_color": "rgba(255, 255, 255, 0.70)",
    "active_color": "#ffd700",
    "emphasis_bg": "rgba(255, 215, 0, 0.18)"
    // Note: y, size, max_words, and max_chars are calculated dynamically from raw video frames and transcript when omitted.
  },
  "motion_physics": {
    "entrance_ease": "power3.out",
    "pop_curve": "back.out(1.3)",
    "damping": 16,
    "stiffness": 180,
    "mass": 1.0,
    "tilt_angle_deg": -1.5,
    "scale_overshoot_pct": 6,
    "camera_punch_scale": 1.10
  }
}
```

---

## 2. Dynamic Frame-Accurate Color Correction Engine (`grade.py`)

Raw camera/phone footage is almost always flat, slightly green/yellow-tinted, or washed out. The color correction engine calculates optimal enhancement parameters **directly and dynamically from the statistical distribution of the video's actual frame pixels**:

```bash
# Calculate dynamic parameters and generate frame-by-frame before/after comparison sheet
python3 "$ENG/scripts/grade.py" dynamic-preview --input "$W/raw/<clip>.mp4" --out "$W/preview/grade-preview.jpg"
```

### Dynamic Frame Parameter Formulation:
| Parameter | Statistical Basis & Formula | Purpose |
|---|---|---|
| **Shadow Floor (`imin`)** | 1st percentile luma ($P_1$) of sampled frame pixels | Anchors clean true blacks without crushing shadow detail. |
| **Highlight Ceiling (`imax`)** | 99th percentile luma ($P_{99}$) of sampled frame pixels | Recovers specular dynamic range without blown-out clipping. |
| **Midtone Exposure (`gamma`)** | $\gamma = \log_{10}(0.45) / \log_{10}(P_{50} / 255.0)$ | Normalizes scene exposure around perceptual 18% middle-grey. |
| **Adaptive Contrast** | Tuned via standard deviation of luminance ($\sigma_Y$) | Applies a natural S-curve proportionate to lighting depth. |
| **Natural Skin Vibrance** | Evaluated from HSV saturation channel mean ($\mu_S$) | Gently lifts healthy skin tones without radioactive oversaturation. |
| **White Balance Calibration** | Red-to-Blue channel ratio ($R / B$) calibrated to 5650K | Neutralizes camera sensor green/yellow tint to daylight neutral. |
| **Micro-Clarity** | Laplacian edge variance filtered at 1080p | Restores subtle micro-detail and edge contrast. |

> **Dynamic Engine Guarantee:** 100% computed from actual frame distributions. Zero artificial stylized filter presets.

---

## 3. Formatting & Overlay Placement Rules

1. **Clean Headroom (Anti-Pattern: Forehead Clutter):**
   - **Never** place sticky headline banners or floating checklist cards over the creator's forehead/hairline (`y: 0.08 - 0.25` in portrait).
   - This looks awkward and suffocating (as seen in bad amateur edits).
2. **Safe Lower Third & Side Zones:**
   - On-screen cards, checklists, and specs must live in the lower half (`y: 0.58 - 0.75`), side panels, or dedicated cutaway scenes.
   - When lower panels appear, captions gracefully step aside to `low_y: 0.86`.
3. **Format Layout Consistency:**
   - The selected format from the 225-Style Taxonomy dictates container borders, background gradient/texture, and aspect ratio padding.

---

## 4. Business Creator Reels Style Direction (Integrated)

For short-form business, creator, interview, finance, entrepreneurship, D2C, and marketing videos (informed by top creators like Raj Shamani, Nitin Joshi, Markets with Jayant, Bypreneurs, D2C by Nikhil, and Marketing with Govind).

### Core Principle: Editorial Credibility First, High-Energy Emphasis Second
Story and evidence carry attention; typography and motion strengthen emphasis without fabricating certainty or obscuring missing facts.

- **Palette Defaults (`styles/business-reels.json`):**
  - Background: `#171717`, Surface: `#252525`, Text: `#F5F1EA`, Muted: `#B9B5AE`, Line: `#4A4845`
  - Accent Punch: `#D9413A` (Red) or Brand Highlight (`#FFD700`, `#00E5FF`)
  - White text on dark/cinematic footage; natural skin tones strictly preserved.
- **Typography & Scripts:**
  - High-legibility grotesque sans (`Inter` 700-800 or `Poppins` 800-900) for display/punch; `Inter` 400-500 for inactive flow.
  - All Hindi/code-switched speech must strictly render in Roman script (Hinglish), never Devanagari.
- **Evidence Contract:**
  - Never fabricate revenue, valuation, conversion, CAC, ROAS, market share, or customer counts.
  - Source labels remain distinct from headlines; distinguish documented facts, attributed allegations, and inferences.
  - Show documents/charts only when they directly support the claim and remain legible long enough to read.

### Motion Patterns & Timing Calibration
- **Pattern 1: Claim → Evidence → Implication:**
  Open on the claim/question → establish entity & context → reveal evidence step-by-step → state the implication.
- **Pattern 2: Text Split Across Visual Contrast:**
  State A in first frame → cut to contrasting state B → complete thought with aligned typography.
- **Pattern 3: Speaker-Led Hook:**
  Start speaker audio directly on the hook → clean medium close-up → modest punch-in (1.08x - 1.12x) on high-value assertion → return to stable frame for dense explanation.

| Motion Element | Duration | Dynamic Behavior |
|---|---:|---|
| Headline Reveal | 180-280 ms | Opacity + subtle vertical settle (`power3.out`). No long intro before hook. |
| Keyword Emphasis | 100-180 ms | Subtle scale pop (`0.90 -> 1.06 -> 1.00`), bold weight shift or badge pill. |
| Callout / Stat Card | 220-360 ms | Opacity + directional slide in lower-third or side canvas. |
| Camera Punch-in | 220-350 ms | Modest scale (1.06x - 1.12x) motivated by a key assertion. |
| Kinetic Chart Build | 350-800 ms | Sequential bar/line growth timed to spoken data points. |
| Scene Transition | 150-300 ms | Brief dissolve or slide; default to clean hard cut. |

### Edit Templates (Content Structures)
- **Template A — Founder / Podcast Moment (15-45s):** Strong hook (0-2s) → speaker context (2-6s) → cause-and-effect narrative → supportive real visuals → clean resolution.
- **Template B — Business / Market Case Study (30-90s+):** Question/claim → entity & timeframe → mechanism in digestible steps → evidence reveal → source prompt & conclusion.
- **Template C — D2C / Marketing Education (15-45s):** Problem/outcome → plain-language framework → concrete sourced example → actionable metric/lesson.
- **Template D — Contrast / Retention Edit:** State A vs State B comparison → legible aligned metrics → causal analysis.

> Full reference documentation: `references/business-reels-templates.md`, `references/business-reels-accounts.md`, and `references/business-reels-audit.md`.

---

## 5. Gate 3: Interactive Style & Color Grade Verification

Before assembling the video or generating components, present `style.json` and the color preview to the user:
1. **Color Grade Preview:** Display `$W/grade-preview.jpg` comparing the raw footage against the proposed preset.
2. **Typography & Font Choice:** Explicitly present font family (from `DM Sans`, `Inter`, `Poppins`, `Google Sans`, `Roboto`), weight hierarchy (400 -> 700 -> 900), and verify zero text-shadow and zero blur by default (confirm if creator wishes to add custom drop shadows, glows, or blurs).
3. **Font-Coloring Hierarchy:** Inactive text color, active highlight accent, punch word badge pill background and text colors.
4. **Color Palette & Contrast:** Background, text, accent, and card glass surfaces.
5. **Motion Dynamics & Physics:** Easing curves, tilt angles, scale overshoot, and entrance springs.
6. **Captions Flow:** Natural phrase mode (`weight-shift` or `caption-highlight`), font pairing, and highlight color.

> Save the verified settings into `$W/style.json` and ensure all downstream components reference these exact tokens. Review with user again at Gate 5 before rendering.
