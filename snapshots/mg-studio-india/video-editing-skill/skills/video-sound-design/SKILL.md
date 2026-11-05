---
name: video-sound-design
description: Picks and places sound effects and a music bed from HeyGen's sound library, each cue anchored to a word. Use when the plan or user asks for music, SFX, "add a pop / click / whoosh", "it feels empty", "too many sounds", "music too loud", and before rendering.
---
# sound-design

> **Styles:** Audio-led styles #188-200 of the 225-style catalog: `references/styles-audio-led.md`.

Silence is the default: a sound earns its place when something on screen would make it, or a reveal needs it. Too many
sounds is the most common first-cut note (eight in a 38 s hook was "way too busy").

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="videos/<project>"
```

| Sound | Allowed on | Volume | Never on |
|---|---|---|---|
| Click | every on-screen cursor click | 0.28 | anything without a cursor |
| Typing | real on-screen typing, exactly that long | 0.22 | anything not a keyboard |
| Pop | a logo or card landing (one per beat) | 0.34 | captions, every card in a list |
| Soft swell / riser | a whiteout or section reveal | 0.2 | copy |
| Cha-ching | a money figure landing | 0.07 | anything louder than a whisper |
| Whoosh | a whip transition, rarely | 0.2 | text of any kind |

The style's `sound` block overrides (business reels: voice first, most reveals silent, no scoring implying unsupported
certainty). One or two sounds per hook; long-form far fewer per minute.

## Source: Local Sound Palette & HeyGen Library

Primary offline source: Curated Sound Palette at `video-editing-skill/sound-palette/` (with 19 pre-trimmed, -3 dBFS peak-normalized forensic & kinetic SFX in `./audio` mapped via `sound-palette.json`).

External source: HeyGen sound library retrieved through HyperFrames' audio engine (`media-use`).
`python3 "$S/heygen-sound.py" --check` (media-use installed? signed in?); sign in with `npx hyperframes auth login` (or
`HEYGEN_API_KEY`); missing media-use: `npx hyperframes skills update media-use`. Not signed in: fallback to local Sound Palette.

Last-resort offline generation (no palette match and no library access): `"${VIDEO_SKILLS:-$HOME/.agents/skills}/video-sound-design/scripts/audiocraft-gen.py"`
`music --prompt "calm lo-fi, soft keys, 90 bpm" --seconds 45 --out "$W/music/bed.wav"` or `sfx --prompt "single soft
click" --seconds 1.5 --out "$W/sfx/click.wav"`, plus `--non-commercial-ok` (MusicGen / AudioGen weights are CC-BY-NC:
**ask the user first** and never use it for monetised or client work). Generated SFX then go through `"$S/sfx-prep.py"`;
every output is logged in `ledger.json` next to it. `--dry-run` shows the plan without loading a model.

## 1. Name, 2. fetch, 3. place

1. Cues in `storyboard.plan.json`, anchored to words, named concretely in English ("soft mouse click", not "sound"):
   `"sfx": [{"id": "click1", "name": "soft mouse click", "at": "@I clicked publish", "volume": 0.28}]`
   (`"@phrase:end"` = its last word; same-frame cues need different ids).
2. `python3 "$S/heygen-sound.py" --plan "$W/storyboard.plan.json" --public "$W/hyperframes" --music "calm lo-fi, soft keys, no vocals, under a talking voice"`
   retrieves each distinct name and the music mood, preps every effect (`sfx-prep.py`: leading silence trimmed so the
   peak lands on the cue, peak -3 dBFS so `volume` is the only mix control), writes `src`/`dur` into the plan, copies the
   bed to `$W/music/`, logs sources in `$W/sound-ledger.json`, and names unmatched cues (rename more concretely).
   Describe the music's feel and job ("tense, minimal, under the hook"); if a later section of the track has a cleaner
   entrance, trim to it.
3. Resolve as usual; the builders turn cues into audio elements (cues without a file, whose phrase was cut, or past the
   end are skipped with a warning). Music is mixed in the master: `render.py ... --music "$W/music/<file>"` (ducked ~16 dB
   under a hook, 18-19 under a body); keep a no-music master.

**Check** after the render: `video-review-gate` lists every sound window; listen at phone volume. Unheard = too quiet or
masked; noticed before the words = too loud; "too busy" = remove, not lower. HeyGen's library terms apply; keep
`sound-ledger.json` with the delivery.
