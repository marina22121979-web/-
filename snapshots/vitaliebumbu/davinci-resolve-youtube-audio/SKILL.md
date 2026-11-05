---
name: davinci-resolve-youtube-audio
description: Make YouTube dialogue clear and correctly loud in DaVinci Resolve (free) by measuring instead of guessing — voice/lav EQ, Fairlight expander/compressor/limiter, -14 LUFS / -1 dBTP normalization ("Optimize to standard"), background music balance, ducking and 3–5 kHz EQ carving. Includes Python (ffmpeg/numpy) measurement tools and Resolve Lua helpers. Use when asked to fix, mix, master, level or normalize audio for a YouTube/talking-head video, or when background music is too loud or too quiet.
---

# DaVinci Resolve YouTube audio

Tools in this folder (run from the folder root):
- `uv run scripts/yt_audio.py loudness|spectrum|peaks|compare|bed ...`
- `resolve-lua/*.lua` — run inside Resolve (Console or a Lua scripting bridge with the `resolve` object).

You usually can't listen to the audio, so **measure, change, render, re-measure**, and let the user make the final call by ear.

## Procedure
1. **Measure the dialogue actually used in the edit.**
   - Get clip ranges with `resolve-lua/export_clips.lua` (it prints JSON).
   - Build a voice file from those ranges with ffmpeg `atrim`/`concat`, or export the dialogue track.
   - Run `loudness`, `spectrum` and `peaks --clips clips.json --start <timeline start frame>`.
   - Report: integrated LUFS, true peak, noise floor, rumble / mud / dullness / resonances, and what the loudest spikes are (speech or clicks).
2. **EQ the dialogue track in Fairlight (UI).**
   - High-pass at 80–100 Hz.
   - Bell cut of -2…-4 dB at the measured mud (usually 250–400 Hz).
   - Narrow cuts only for resonances above ~4 dB.
   - +1…+2 dB high shelf or wide bell near 5 kHz if the voice is dull.
3. **Set the level before Dynamics.**
   - Raise quiet dialogue clips with `set_dialogue_clip_gain.lua` (`AudioVolume`) so speech sits around -20 LUFS.
   - Dynamics: expander just above the noise floor (e.g. -50 dB), compressor -30 dB 2:1 (attack 1.4 ms, release ~90 ms), make-up 0, limiter -2 dB for clicks.
   - Never pair a low limiter with lots of make-up gain.
4. **Deliver → Audio Normalization (UI):** Normalize Audio, **Optimize to standard**, Standard YouTube (-14 LKFS, -1 dBTP).
   - "Normalize to standard" stops as soon as the loudest peak reaches -1 dBTP, so one click can leave the video ~17 dB too quiet.
5. **Verify.**
   - Run `audio_test_render.lua`, then `yt_audio.py loudness` on the result (target ≈ -14 LUFS, ≤ -1 dBTP).
   - Run `compare raw_voice.wav mix.wav`: a median extra reduction of about 0–2 dB and a 90th percentile ≤ 6 dB means natural speech.
   - Then run `restore_video_render.lua` and re-check the normalization checkbox in the UI.
6. **Music.**
   - Under voice ≈ 16 dB below speech (10–20 dB range). Intro without voice ≈ 7–8 dB below speech level.
   - Carve the music with a bell at 3–5 kHz, -12…-15 dB, Q ≈ 0.8: clip Inspector → Audio → Equalizer, or `yt_audio.py bed --carve 4000`.
   - Re-measure the intro-music vs speech gap after the dialogue processing, and adjust the music clip volume.
7. **Report** what changed (values, clips, measured before/after) and ask the user to listen. Offer to save a Fairlight Global Track Preset.

## Facts (Resolve 21.1 free)
- Scriptable:
  - clip `AudioVolume` (-100…+30 dB);
  - render settings and render jobs;
  - `bmd.wait()` for polling.
- Not scriptable:
  - Fairlight EQ, Dynamics and FX;
  - Deliver audio normalization;
  - volume keyframes;
  - clip EQ.
- Resolve's Lua has no `io`: return or print data instead of writing files.
- After an audio-only test render, restore the format with `SetCurrentRenderFormatAndCodec("mov","H264")` and set `ExportVideo=true`. Delete test jobs.
