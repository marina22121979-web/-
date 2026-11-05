---
name: video-audio
description: Clean and master dialogue locally with FFmpeg and one optional neural enhancer; use before video assembly. Never promise complete echo removal or speaker isolation.
---

# Video Audio

Goal: clearer, natural speech approaching podcast quality. Preserve the source; never overwrite it. Process the assembled mix once for final loudness.

## 1. Inspect Tools and Source

Verify local tools:
```bash
set -eu
ENG="${VIDEO_ENGINE:-$HOME/.agents/skills/video-pipeline/engine}"
command -v ffmpeg
command -v ffprobe
command -v sox
ffmpeg -hide_banner -filters 2>/dev/null | grep -E 'afftdn|arnndn|loudnorm|alimiter|highpass|acompressor|deesser|equalizer' || true
INPUT="/path/to/input"
```

---

## 2. The Dynamic Identification Process (Input-Driven Calibration)

Never apply hardcoded frequencies, blind mic extraction, or static noise sample timestamps. Dialogue audio varies across devices, speakers, and acoustic spaces. 

> [!IMPORTANT]
> **Virtual Environment (STRICT)**: ALWAYS execute scripts using the project's virtual environment (`"$PROJECT/.venv/bin/python3"`). Never invoke system python.

```bash
"$PROJECT/.venv/bin/python3" "${VIDEO_SKILLS:-$HOME/.agents/skills}/video-audio/scripts/audio-analyze.py" "$INPUT" --json > acoustic_profile.json
```

The analyzer inspects the raw signal and dynamically identifies:

| Acoustic Variable | Measurement Method | How It Derives Settings |
|---|---|---|
| **Channel Routing** (`CH_FILTER`) | Compares Channel 0 vs 1 RMS & speech band (300-3500 Hz) energy. | If asymmetric (e.g. phone with mouth mic vs room mic): selects dominant speech mic (`pan=mono\|c0=c0` or `pan=mono\|c0=c1`). If symmetric: downmixes `pan=mono\|c0=0.5*c0+0.5*c1`. If already mono: `anull`. |
| **Room-Tone Noise Window** (`NOISE_START`, `NOISE_DUR`) | 400ms sliding window scan across pauses to locate the quietest inter-phrase room tone floor (above digital silence). | Gives the exact timestamp to sample room hiss for SoX without clipping speech onsets or vocal tails. |
| **Voice Fundamental ($F_0$) & Highpass** (`HIGHPASS_HZ`) | Autocorrelation on voiced speech frames to detect the speaker's true pitch fundamental $F_0$. | Sets high-pass cutoff dynamically to $\max(75, F_0 - 25\text{ Hz})$ to kill sub-rumble without thinning male or female vocal fundamentals. |
| **Proximity Warmth** (`WARMTH_HZ`) | Centers warmth boost directly at detected $F_0$ ($100-150\text{ Hz}$ male, $180-240\text{ Hz}$ female). | Boosts the speaker's natural vocal chest resonance (+1.0 to +1.5 dB) rather than a blind arbitrary frequency. |
| **Room Standing Modes** (`NOTCH_FILTERS`) | High-resolution spectral scan across the $120-750\text{ Hz}$ room reverberation range to detect narrow stationary spikes ($\ge 2.8\text{ dB}$ above moving spectral envelope). | If standing modes exist: generates targeted surgical notches (`equalizer=f=$F:t=q:w=3.5:g=-$G`). If the acoustic space is clean: generates **no notches** to preserve phase integrity. |
| **Speech Level & Dynamics** (`COMP_THRESH`) | Measures 90th percentile voiced speech RMS. | Dynamically calibrates leveling compressor threshold to `speech_rms - 4 dB` to even out phrasing without over-squashing dynamics. |

---

## 3. The 2-Stage Dynamic Processing Pipeline

Once values are identified from the input, execute the 2-Stage Stacked Pipeline:

```
Raw Camera Audio
  │
  ▼ [Stage 1: Dynamic Clean Base]
Mic Selection (CH_FILTER) ──► Dynamic Highpass (HIGHPASS_HZ) ──► Measured Room Notches (NOTCH_FILTERS) ──► RNNoise (arnndn) ──► Dynamic SoX Noise Sample (NOISE_START)
  │
  ▼ [Stage 2: Calibrated Vocal Presence & Broadcast Master Stacked on Top]
Proximity Warmth (WARMTH_HZ) ──► Articulation & Presence (2.8k & 4.2k) ──► Studio Sheen (10k) ──► Calibrated Optical Leveling (COMP_THRESH, release 70ms) ──► 2-Pass Loudnorm (-14 LUFS)
```

### Stage 1: Extraction & Dynamic Baseline Denoising

```bash
# 1a. Extract primary speech channel, apply dynamic highpass and detected room notches
# (If no room resonances were detected, NOTCH_FILTERS is omitted)
ffmpeg -hide_banner -y -i "$INPUT" -vn \
  -af "${CH_FILTER},highpass=f=${HIGHPASS_HZ}:poles=2${NOTCH_FILTERS:+,${NOTCH_FILTERS}}" \
  -c:a pcm_s24le stage1_notched.wav

# 1b. Neural Speech Denoising & Reverb Suppression (RNNoise)
# Uses the sh.rnnn GRU model at ~/.config/video-skills/rnnoise/sh.rnnn
ffmpeg -hide_banner -y -i stage1_notched.wav \
  -af "arnndn=m='$HOME/.config/video-skills/rnnoise/sh.rnnn':mix=0.85" \
  -c:a pcm_s24le stage1_neural.wav

# 1c. Sample room noise from the dynamically identified quietest pause and apply gentle SoX reduction
sox stage1_neural.wav noise_sample.wav trim "${NOISE_START}" "${NOISE_DUR}"
sox noise_sample.wav -n noiseprof room.prof
sox stage1_neural.wav stage1_clean_base.wav noisered room.prof 0.15
```

### Stage 2: Calibrated Vocal Presence & Broadcast Leveling Stacked On Top

Run directly **on top of `stage1_clean_base.wav`** to add in-your-face creator presence, consonant articulation, chest warmth, and platform loudness:

```bash
# 2a. Pass 1: Measure loudnorm parameters with calibrated presence EQ and optical compression
ffmpeg -hide_banner -y -i stage1_clean_base.wav \
  -af "${NOTCH_FILTERS:+,${NOTCH_FILTERS},}equalizer=f=${WARMTH_HZ}:t=q:w=1.5:g=1.5,equalizer=f=2800:t=q:w=1.2:g=2.5,equalizer=f=4200:t=q:w=1.5:g=3.0,highshelf=f=10000:g=2.0,deesser=i=0.35:m=0.5:f=0.5,acompressor=threshold=${COMP_THRESH}dB:ratio=2.2:attack=15:release=70:knee=3:makeup=1,loudnorm=I=-14:TP=-1.2:LRA=7:print_format=json" \
  -f null - 2>&1

# 2b. Pass 2: Render final 320k MP3 master using measured JSON values
ffmpeg -hide_banner -y -i stage1_clean_base.wav \
  -af "${NOTCH_FILTERS:+,${NOTCH_FILTERS},}equalizer=f=${WARMTH_HZ}:t=q:w=1.5:g=1.5,equalizer=f=2800:t=q:w=1.2:g=2.5,equalizer=f=4200:t=q:w=1.5:g=3.0,highshelf=f=10000:g=2.0,deesser=i=0.35:m=0.5:f=0.5,acompressor=threshold=${COMP_THRESH}dB:ratio=2.2:attack=15:release=70:knee=3:makeup=1,loudnorm=I=-14:TP=-1.2:LRA=7:measured_I=<input_i>:measured_TP=<input_tp>:measured_LRA=<input_lra>:measured_thresh=<input_thresh>:offset=<target_offset>:linear=true" \
  -c:a libmp3lame -b:a 320k mastered.mp3
```

---

## 4. Critical Engineering Rule: Preventing "Word Buzzing"

**Never apply aggressive fast-attack gates (`attack < 10ms`, `release < 80ms`) to dialogue.** 

Speech fundamentals ($F_0 \approx 100-250\text{ Hz}$) have acoustic wave periods of 4-10ms. When an amplitude gate opens and closes rapidly, it modulates the waveform within individual pitch cycles, producing a harsh buzz, edge flutter, or vowel sputtering at word boundaries. 

**Process rules:**
1. Rely on continuous frequency-domain neural masking (RNNoise `arnndn`) and SoX spectral subtraction (`noisered`) for noise/reverb decay suppression.
2. Use smooth, optical-style leveling (`attack=15-20ms`, `release=70-140ms`, `knee=3-4dB`) that maintains natural vowel decay and zero edge buzz.

---

## 5. Verification and Acceptance

Always verify the mastered MP3 with `ebur128` and Whisper transcription:

```bash
ffmpeg -hide_banner -i "mastered.mp3" -af "ebur128=peak=true" -f null -
whisper-cli -m ~/.cache/whisper.cpp/ggml-large-v3-turbo.bin -f "mastered.mp3" --no-timestamps -l en
```

Must satisfy:
- Integrated Loudness: `-14.0 ± 0.5 LUFS`
- True Peak: `<= -1.0 dBTP`
- Zero word buzzing / gate chatter
- 100% speech transcription accuracy preserved with zero lost word endings

---

## Echo & white-noise cleanup tool (`tools/voice-clean.py`)

For rooms with audible echo, run this before `audio-chain.py clean` (it replaces the clean pass) and before transcription:

```bash
"$PY" "$SKILL/tools/voice-clean.py" "$W/raw/<clip>.MOV" --video "$W/raw/<clip>-sdr.mp4" --out "$W/raw/<clip>-clean.mp4" [--keep <tmpdir> --reuse]
```

`$SKILL` is this skill's folder; `$PY` the project `.venv/bin/python` (needs `nara_wpe soundfile scipy`, installed by `install.sh`).
Chain: WPE multi-mic dereverb (uses both phone mics) → statistical late-reverb suppression (`tools/late-reverb.py`,
RT60 0.5 s, −10 dB floor) → DeepFilterNet3 (`deep-filter`, downloaded by `install.sh` to `~/.config/video-skills/bin`,
or `$VIDEO_DEEPFILTER`) → 80 Hz high-pass, −3 dBFS peak, muxed onto the picture. Measured on an iPhone office take:
noise floor −70 → −82.6 dBFS, SNR 49.6 → 63.4 dB, reverb tail ~7 dB lower at 200 ms. Report echo as *reduced*, never
removed; check timing with a cross-correlation (it stays sample-aligned) and spectral balance before mastering.
