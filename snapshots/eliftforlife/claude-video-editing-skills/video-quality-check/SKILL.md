---
name: video-quality-check
description: Check raw footage and a finished edit for the problems that make AI-edited videos look flat, soft or noisy and sound uneven - HDR footage, range mismatches, stacked compression, upscaling, loudness and true-peak. Use before editing new footage and before uploading a final video.
---

# Video quality check

Run this on the raw takes **before** editing and on the final file **before** uploading. Report what you find in plain words and what to change.

## Raw footage

```
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,pix_fmt,color_range,color_transfer,color_primaries -of compact <take>
```

- **HDR.** `color_transfer=arib-std-b67` (HLG) or `smpte2084` (PQ) means HDR. Treated like normal video it comes out flat and grey. Best fix: tell the creator to turn off HDR Video (iPhone: Settings › Camera › Record Video). Otherwise tone-map to SDR BT.709 once, at the very first step.
- **Range.** iPhone SDR is often full range (`yuvj420p`, `color_range=pc`). Convert to limited (tv) range once, explicitly, or blacks and whites get crushed or washed out.
- **Brightness.** Measure the average luma (`signalstats`, YAVG). Under ~35/255 means a dim room. Fix the light, don't add darkening grades or vignettes on top.
- **Resolution.** 1080p is enough for talking heads. Keep punch-ins modest (≤1.15×), since every zoom is an upscale.
- **Audio.** Check loudness (`ebur128`) and look for clipping in the raw file: a sample peak at 0 dBFS means the mic clipped and no edit can fully fix it.

## The edit pipeline

Count the lossy encodes from raw to upload. Every one costs detail, worst in dark shadows.
- Keep intermediates near-lossless: x264 CRF ≤ 10, 10-bit.
- Composite graphics in **one** final pass. Don't round-trip frames through JPEG.
- Don't add animated grain. It eats bitrate and turns to blotches after YouTube's encode.

## Final file

- Video: H.264 High, yuv420p, BT.709 tags, CRF ~14, `+faststart`.
- Loudness: about -14 LUFS integrated. True peak ≤ -1 dBTP: limit with oversampling (e.g. `aresample=192000,alimiter,aresample=48000`), since sample-peak limiting alone can still overshoot after AAC.
- Music under speech: about 18–22 dB below the voice.
- **Re-transcribe the final voice track** and read it top to bottom. It catches clipped first words, repeated phrases and stray syllables that you'll miss by ear.

Report each problem with the measured number, why it matters, and the one-line fix.
