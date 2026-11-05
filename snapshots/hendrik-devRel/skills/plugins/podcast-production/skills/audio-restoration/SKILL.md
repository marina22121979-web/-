---
name: audio-restoration
description: Repair electrical buzz, hiss, short clicks, and brief vocal backchannels in speech recordings using local processing. Use for podcast WAV cleanup and shared-mix reaction-reduction trials with preserved timing, separate copies, and matched previews.
---

# Audio restoration

Turn noisy speech recordings into reviewable cleaned copies. Combine repair methods according to the measured problem; a successful preset from another recording is a starting point, not a universal setting.

## Inspect the actual recording

- Read the user-specified files first. Reading a cloud-backed local file may hydrate it; confirm the complete file is readable before processing. If local access fails, use the available Drive workflow for the requested files. Keep generated audio in a task output directory and leave originals intact.
- Record channel count, sample rate, subtype, frame count, peak, and duration. Inspect levels over time, spectra from multiple quiet intervals, and short transients. Check noisy speech as well as pauses. A clipped signal, continuous tonal hum, broadband hiss, and isolated clicks need different treatment.
- Treat a mains-like harmonic pattern or sharp transient as signal evidence, not proof of a physical fault. Hum can drift; blindly notching every exact 50/60 Hz harmonic can damage speech and miss the interference.
- Use timestamps supplied by the user. When the complaint is unclear, ask for a representative moment while continuing file access and diagnosis. Do not postpone an otherwise useful first trial solely for that optional detail.

## Choose the pilot workflow

For brief vocal reactions such as "mm-hmm" in a shared mix, read [shared-mix backchannel trials](references/shared-mix-backchannels.md). That workflow distinguishes a local gain dip between phrases from overlapping-speech treatment; the noise-profile recipe below does not isolate a speaker.

## Build an electrical-noise pilot

The local helper is [scripts/restore_audio.py](scripts/restore_audio.py). Read [the workflow and CLI guide](references/workflow.md) for dependencies, supported formats, commands, and parameter meanings. It provides analysis, a configurable repair pass, matched previews, and numerical reports. Use another appropriate tool when the helper's supported inputs do not fit the task.

1. Choose representative excerpts containing the suspected interference, normal speech, quieter speech, and pauses. Keep source timestamps so pilot and full-file settings can be compared.
2. Build a separate noise profile for each microphone. Prefer verified noise-only regions or distributed quiet intervals with robust aggregation. Startup silence can have a different floor; brief words, breaths, and clicks can contaminate a quiet reference. Inspect the reported candidate intervals before using automatic selection.
3. If short spikes are present, test de-clicking before spectral denoising. Padding and exact trimming prevent the de-clicker's startup transient from changing the delivered boundaries. Do not add de-clipping simply because clicks exist.
4. Apply spectral reduction with conservative settings first. Existing gate/expansion can make inactive-microphone references underestimate the noise during speech. Raise the profile only after comparing a pilot; smooth the gain changes and cap attenuation to limit musical or watery artifacts. Check low-level consonants and word endings, not only aggregate speech level.
5. Compare at the same gain. Keep the original, cleaned, and removed-sound excerpts available. If listening is unavailable, state that measurements alone do not establish naturalness. User listening feedback is additional evidence, not a guarantee for other files.

The [validated worked recipe](references/workflow.md#validated-worked-recipe) records the two-stage settings that succeeded on a pair of long mono podcast recordings. Preserve that recipe as an option while tuning new material from its own evidence.

## Export and verify

- Preserve the original sample rate, channel layout, supported bit depth, gain, and exact frame count unless the user requests a different deliverable. Do not normalize full-length replacement stems as part of interference repair. A pilot may be shorter, but must report its original offset.
- Verify complete decoding, finite samples, clipping/headroom, and frame count. Check alignment on speech near the beginning, middle, and end. For chunked processing, compare seams with a longer-context render; a matching duration alone does not prove alignment.
- Report noise measurements with their selection criteria. An attenuation cap is not achieved overall reduction; quiet-section improvement is not an SNR measurement during speech. Low RMS change alone does not prove preserved intelligibility.
- Deliver the requested pilot or full-length cleaned files plus short original-then-cleaned previews at matched gain. Preview boosts are for listening only. Give source timestamps and a concise explanation of the actual treatment and verification limits.
- Keep settings and reusable scripts; remove expendable intermediates after verification.
