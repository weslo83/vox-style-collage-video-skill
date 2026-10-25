---
name: vox-style-collage-video
description: >-
  Create narration-led paper-collage explainer videos with Unsora, or draft their
  beat maps and shot prompts. Use for Vox-style editorial collage videos from
  scripts, facts or ideas. Generation requires connected Unsora tools; planning
  and prompt-only requests do not.
---

# Vox Collage Video

Turn an approved script into an editorial paper-collage explainer, or deliver
only the shot prompts when that is what the user requested. Preserve the user's
facts, intended message, chosen tools and publication boundary.

The visual language is photographic cut-outs with torn edges on an off-white
newsprint ground, one bold accent, argument-carrying type, infographic marks and
limited-frame motion. Narration sets the timing. This is an aesthetic reference;
do not imply that the output is produced or endorsed by Vox.

## Choose the scope before choosing tools

- **Planning or prompts:** read the brief and produce the requested beat map,
  script or shot prompts. Unsora, credits, narration audio and FFmpeg are not
  prerequisites for this work.
- **Generation:** discover the live Unsora image/video tool schemas and confirm
  the connection before spending credits. Check music tools only when generated
  music is requested. Do not silently substitute another generator. If tools are
  unavailable, finish the useful planning and identify the missing capability.
- **Assembly of existing assets:** use supplied clips and audio with local
  FFmpeg/ffprobe. Do not require new generation to repair timing or mix audio.

Model names, reference slots, duration limits and polling examples in the
references are defaults from the original workflow. Inspect current tool schemas
before calls; do not promise availability, exact cost or a fixed turnaround from
these examples. Use the session's actual TTS capability or supplied narration;
never claim a generator produced narration when it did not.

## Prepare a concrete production plan

Infer orientation, tone and length from the request. Resolve only missing choices
that affect production: script, aspect ratio, one accent color, narration source,
and music (none, supplied, or generated). A generated music bed is a paid option,
not an automatic extra. Honor choices and authorization already given.

Read [beat-mapping.md](references/beat-mapping.md) to segment narration. Each shot
communicates one point, with a type card stating it and narration explaining it.
Track recurring subjects and reference sheets without creating speculative
assets. Identify unsupported factual claims and illustrative statistics before
they become narration or charts; never invent citations or archival provenance.

Present the shot table, full narration draft, asset plan, approximate runtime,
orientation, accent, selected tools and expected paid operations. Make the scope
and spend reviewable before generation. Obtain approval for choices or costs not
already authorized; do not repeat an approval the user already supplied for this
same plan. Additional paid rerolls need to stay within that approved scope.

## Voice first, then lock the edit

Use supplied audio unchanged as the original. For TTS, audition one voice if
needed, then synthesize per beat and retain every completed segment. For a silent
cut, type carries the argument and no TTS is required.

Measure actual audio duration, then allocate each edit window with lead and tail
space. Round required generated duration **up**, subject to the live model's
limits; split an overlong beat before spending on an impossible clip. Keep
`seconds` (final edit window) distinct from generated clip duration. Do not use a
word-count estimate as proof that narration fits. Exact splitting, timing fields
and validation are in [pipeline.md](references/pipeline.md).

## Art-direct each shot

Read [style-dna.md](references/style-dna.md) before writing visual prompts. It
contains the visual system, templates, reference-sheet designs and checklist.
For each shot, deliver:

1. The point, narration line, type card and recurring asset bindings.
2. Duration, composition, accent use, motion and audio intent.
3. A hero-frame prompt and an animation prompt in separate code blocks.

Keep image and video aspect ratios identical. Reference-slot numbers must match
the live call, especially when a starting image occupies the first slot. The
hero image can describe the resolved layout, but an image supplied as `image` is
still a **starting frame**. A prompt cannot make it become an end-frame constraint.
For an assembly reveal, use an approved empty/partial starting plate and, only if
supported, a separate end-frame parameter; otherwise plan motion that works from
the finished composition. Never chain unrelated shots for a discrete-card edit.

Keep narration out of video-generation prompts. Request only the intended foley
and no generated voice or music. Check exact spelling, numbers, cropping and
visual identity in outputs; repair essential type with local overlays when
appropriate rather than treating generated text as verified.

## Generate and preserve progress

Follow [pipeline.md](references/pipeline.md) for calls, manifest fields, local
assembly and verification. Write generation IDs immediately after acceptance,
before polling. Save the manifest atomically, retaining the previous valid copy.
A timeout means completion is unknown: poll the existing ID before resubmitting.
Do not create duplicate paid jobs merely because a wait ended.

Keep successful sheets, narration, images and clips. Repair only the failed
stage, with bounded retries; stop on authentication, exhausted credit or content
rejection rather than repeatedly submitting the same request. A `done` flag is
not a substitute for checking the local asset still exists and decodes.

## Assemble and verify

Prepare clips to a common resolution, frame rate, codec, time base and audio
layout. Use manifest order, never a wildcard that can include raw or old clips.
The helper validates timing and generates an explicit concat list:

```sh
python3 scripts/prepare_timeline.py /path/to/project/shots.json \
  --probe --output-dir /path/to/project/assembly-check-01
```

The output directory must be new. The helper reads sources without changing them and writes only its validation outputs;
it does not call providers, render media or declare visual quality.
Use `timeline.json` for narration offsets. Read the pipeline's mix graph: split
the voice stream for sidechain and audible narration, and bound audio to the
picture duration so short foley does not truncate the film.

Check final duration against the sum of edit windows, video/audio streams,
orientation, loudness/clipping, narration intelligibility, type and key frames.
Watch the completed cut, including transitions and the ending. Deliver the final
MP4 and explain any unverified stage; preserve the workspace for revisions.

Publishing is separate from generation. Prepare the final media, caption,
account and schedule for review. Post only within explicit authorization and
confirm the resulting post state; a queued post is not a published one.
