---
name: product-story-editing
description: Shape recorded product or company interviews into coherent vision, mission, origin, or product stories using take comparison, source-linked transcript selects, and context-preserving edits. Use when the main task is constructing a narrative from interview material and a brief or script.
---

# Product Story Editing

Turn the recorded material into a supported story for the intended audience. Build the content rough cut before graphics. A strong continuous take may serve the story better than a hybrid assembled from many passages.

## Establish what was recorded

Identify source files, speakers, camera coverage, and recording continuity. Several WAVs may be sequential chunks or backups rather than isolated microphones. Two camera angles may show the same subject rather than one participant each. Resolve these facts from media evidence; filenames and diarization labels are insufficient.

Use a transcript to inventory takes before selecting lines. Separate presenter performances, interviewer questions, director/script read-throughs, rehearsal, resets and usable conversation. Identify who actually speaks each candidate; a polished script read aloud during direction is not automatically the intended performance. Retain raw ASR and corrected production text separately, with unresolved names, product terms, numbers and negations marked.

For media probing, synchronization, audio, grading and native construction, use the available `premiere-podcast-editing` skill. This skill adds editorial decisions rather than a second native editing toolkit.

## Test the desired story against the source

Derive the audience, purpose, intended ending and delivery constraints from the user's brief and any supplied script. The script guides searches and structure; it does not prove a sentence was spoken or a product capability exists.

Distinguish recorded statements, script-only beats and editorial interpretation. Preserve whether a statement describes a past event, current capability, proposal or future intention. Do not strengthen it through reordered dialogue, captions or supporting visuals. Product spelling and availability can require separate confirmation even when the spoken passage is clear.

Use an origin-to-direction arc only when the source supports both. A market problem is not a company founding story. When history, examples or transitions are missing, record the gap and the available narrower story; do not invent connective narration or imply a historical sequence.

## Compare takes and build the selects

When the user asks for natural delivery, make performance a selection requirement. Prioritize answers from actual conversation over polished teleprompter takes, even when the reading has a cleaner narrative. Inspect the take's surrounding direction, original question, eyeline, gestures and cadence; a fluent transcript or a side-angle crop does not establish spontaneous speech. An uninterrupted interview answer can be the continuous baseline. Do not let minimal joins or unused-source targets override the requested delivery.

Review the strongest complete performance as a baseline. Compare a hybrid for a concrete improvement: clearer reasoning, a useful qualification, a more natural exchange or a specific example. Do not replace a coherent passage merely to increase cut count or because it was scripted. Transcript fluency and crew comments help locate candidates; delivery quality requires listening and picture review.

Read [selects and edit-map contract](references/selects-and-edit-map.md) when documenting a shortlist or preparing a rough assembly. Link every beat to original source intervals, its question/context and the reason it belongs. Recommend one assembly when requested, with useful alternatives and their rejection reasons recorded separately. Treat target duration as a constraint rather than permission to pad or amputate a complete thought.

## Preserve answer dependencies

Remove a question only when the answer supplies its own subject and necessary premise. Check openings such as “yes,” “that” and “because,” as well as references to earlier claims. Retain the original question with its answer when it carries a material distinction; never attach an answer to another question.

For a presenter-only request, keep prompts in the source ledger and omit them from the film. Choose self-contained answers or complete clauses that retain their own conditions and subjects. If a question is essential to an answer's meaning, use another answer instead of forcing the question back into the cut. Remove question acknowledgments and check the tail for the interviewer's next “okay” or follow-up; broad ASR segment boundaries often contain both speakers. Do not label fragments as one continuous original answer.

Keep qualifications, negations, attribution and meaningful uncertainty. A later risk-awareness statement does not promise risk elimination. Reordering can create an unsupported causal or chronological link even when every sentence is verbatim. Check each new join against both original contexts. Label any supplied context card as editorial wording rather than a quotation.

Use ASR times to find passages, then refine boundaries with listening and waveform evidence. Keep complete words and clean handles. A self-repair may be shortened only if the resulting statement preserves the speaker's intended meaning and sounds natural.

## Assemble and review the content cut

Keep per-file source clocks and the verified synchronization map distinct from output time. Reordered selections need an ordered source-to-output map; a later WAV does not inherit the previous file's duration as an offset without measured evidence.

Choose camera changes from actual framing, performance and synchronized coverage. An alternate angle can support a thought transition or cover a speech edit; it need not show a different person. Preserve real reactions in their source context rather than borrowing agreement from elsewhere. Keep continuous dialogue independent of camera cuts and use J/L cuts only with the source relationship intact.

Review the complete rough story for understandable subjects, supported progression, natural joins and a resolved ending before polishing typography, music or B-roll. Use `podcast-trailer-editing` when the requested deliverable becomes a trailer, standalone social clip or kinetic treatment. Follow the existing native workflow for construction and export checks.

Hand over the versioned content cut, source-linked map, substantial choices and unresolved gaps. Distinguish transcript planning, listening, sampled picture checks, native assembly and rendered review. This skill's transcript/selects workflow has been exercised; it adds no independently tested native-render procedure.

## Explore an alternate cut and prepare a re-record

When the user asks for another version, define the new story progression before choosing more excerpts. Compare source overlap with the accepted cut; different camera angles or captions alone do not make a materially different content edit. Test whether a few longer passages can carry the argument with fewer changes between scripted delivery, interview questions and explanation. Preserve the original dependencies of connective phrases such as “that's where” and “then.”

For a practical product story, a sequence of audience decisions can organize otherwise abstract material: what deserves attention, what a change would do, and what to learn after it ships. Use that structure only when the recording supports it. Compare the result with a continuous-take baseline and record why additional passages improve the story.

Deliver the new cut's output-clock transcript alongside the complete source-clock transcript. Keep the recorded scripted take, related written reference documents and newly proposed re-recording copy distinct. Preserve resets and alternate takes in the source package. A transcript model can smooth a self-repair; retain conflicting evidence instead of silently polishing it into a quotation. Propose targeted pickups for missing examples, transitions or history, then one uninterrupted performance of the agreed script.

## Add animated captions to an accepted content cut

Use `podcast-trailer-editing` for native speech-timed typography. Align corrected caption copy to the accepted output audio, retaining raw ASR, spelling evidence and timing uncertainty separately. A script can resolve a product's spelling, but it cannot prove that a disputed word was spoken. Preserve the accepted picture and dialogue timing while adding the graphics layer.

Adapt caption placement to the actual camera coverage. A landscape presenter film can use different side blocks for frontal and tight angles; a portrait Shorts layout should not be transferred without checking faces and gestures. Keep complete phrase layouts fixed as words arrive, carry already-visible words across camera changes, and reserve larger type and drawn accents for a few important ideas. If technical wording will not fit at a readable size, reflow or shorten the caption group without losing words. Deliver the preview, editable graphics source, caption file and timing map; record native layout checks separately from listening and visual acceptance.
