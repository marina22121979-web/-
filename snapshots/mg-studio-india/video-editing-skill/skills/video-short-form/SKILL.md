---
name: video-short-form
description: Finds standalone moments in a longer video and cuts them into vertical Shorts, Reels or TikToks with face-tracked framing. Use when the user asks for Shorts, Reels, clips, vertical versions, "find the best moments" or "make a 30-second version".
---
# short-form

A Short must stand alone: a stranger scrolling, sound off, decides in about a second. Pick by that test, cut cleanly,
edit each as its own vertical video. Starts from the approved flat cut (`$W/hyperframes/input-video.mp4`, gate 2 passed) and
its `transcript.json`.

```bash
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"; S="$ENG/scripts"; W="videos/<project>"
```

## 1. Candidates

Read the flat transcript; keep moments that pass all of:
- **A hook in the first sentence** (claim, question, number, surprise). If the best line is mid-moment, open on it and
  cut to the explanation (two ranges).
- **One idea, paid off** in 20-60 s (YouTube allows 3 min, but a longer Short is usually two).
- **No outside context:** no "as I said", "in this video", "the second tool", unexplained names.
- **An ending:** payoff, punchline, or a line that loops to the first frame; not a trailing "so...".
- **Alive in 9:16** (watch sheets): not a stretch where the speaker leaves frame or the point needs a full-width screen
  (or plan a split-screen).

Score hook, standalone clarity and payoff (high/medium/low); show the top 3-5 with opening line, closing line, length
and why. Part of gate 1 when planned, else its own approval. Never cut a Short the user hasn't picked.

## 2. Cut

`python3 "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-short-form/scripts/make-short.py" --flat "$W/hyperframes/input-video.mp4" --transcript "$W/transcript.json" --out-dir "$W/shorts/01" --range "@the real reason..@nobody tells you"`
Ranges are phrases (`@first words..@last words`) or seconds (`412.3-438.9`); edges snap to whole words with a short
lead-in and tail. Open on the best line with two ranges (`--range "@this one setting..@doubled my views" --range "@let me explain..@and that's why"`),
without repeating the hook line. Writes `hyperframes/input-video.mp4`, `cut-list.json`, `cut-map.json`, `short.json`; warns
over 60 s or under 10 s.

## 3. Its own edit

Each `shorts/<n>/` is a project: `program: "short"`, `aspects: ["9:16"]`, `audio_preset: "shorts"`.
1. `video-transcribe` its flat file (pass 2).
2. `video-take-geometry`: `reframe.py` to 9:16 on the face (static per shot) → `hyperframes/input-9x16.mp4` as the video.
3. Its own `storyboard.plan.json` under the Short rules (`video-plan-storyboard` program types): 1080x1920, never a centre crop,
   word-exact captions, something new every 1.5-3 s, punch-ins on emphasis, one open loop; resolved against its own
   transcript.
4. `video-captions`, `video-format` (owns the 9:16 safe zones), `video-motion-graphics`, `video-sound-design`, `render --resolution portrait
   --audio-preset shorts`, `video-review-gate`.

List each Short in the parent `project.json` (`"shorts"`: folder, ranges, length, status).
