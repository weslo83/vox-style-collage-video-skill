# Pipeline reference — Unsora generation · VO · ffmpeg

Exact mechanics for Phases 4–8. The defining split: **all image/video/music
generation is Unsora through Unsora MCP**; **the voiceover comes from outside
Unsora** (it has no TTS) — either a file the user supplies or whatever TTS tool is
connected in the session; **assembly and mix are ffmpeg**. The user opted into the
VO source at the front door, so act on that choice directly; if a call returns an
auth error, surface it and the user re-authenticates.

This skill assumes it is running in Claude, OpenClaw, or Hermes Agent with Unsora
MCP connected for generation. Prompt-only planning and local assembly do not require Unsora. Check live schemas before paid calls: model names, parameter limits, slot ordering and wait arguments below are examples, not a current API guarantee.

Contents:
1. Workspace layout
2. Unsora — reference sheets
3. Unsora — hero frame
4. Unsora — clip
5. Unsora — music
6. Voiceover — supplied file
7. Voiceover — session TTS tool
8. Manifest schema
9. ffmpeg — concat
10. ffmpeg — VO timing + duck/mix
11. ffmpeg — brand-bug overlay (optional)
12. Verification
13. Resume after failure
14. Optional posting

---

## 1. Workspace layout

```
<agent-workspace>/vox-collage/
├── shots.json           # manifest — source of truth for resume
├── sheets/              # reference sheets, generated before any shot
├── frames/              # hero frames  (shot_01.png …)
├── clips/               # animated clips (shot_01.mp4 …)
├── vo/                  # per-line voiceover (vo_01.mp3 …)
├── music.mp3            # only if a bed was requested
├── logo.png             # only if a brand bug is used
├── concat_list.txt
├── cut.mp4              # stitched, foley only
└── final.mp4            # VO + music mixed  (the deliverable)
```

Deliver `final.mp4` and retain the workspace and manifest for revisions. Never overwrite originals when downloading, splitting or mixing; use distinct output names and promote a verified candidate to the deliverable.

---

## 2. Unsora — reference sheets (`create_image`, only if the tally flagged one)

| Param | Value |
|---|---|
| `prompt` | The sheet prompt (character/place format from `style-dna.md`), verbatim |
| `model` | `nano-banana-pro` |
| `aspectRatio` | `"16:9"` — sheets are always 16:9 regardless of the film's ratio |
| `referenceImages` | Omit, unless the user supplied a design reference to match |

Then `Unsora AI:wait_for_image` (`generationId`, `intervalSeconds: 5`,
`maxAttempts: 60`). Record the URL in the manifest `assets` block and
`curl --fail --location --retry 2 -o sheets/<name>.png "<URL>"`. Show each sheet to the user before shots.

---

## 3. Unsora — hero frame (`create_image`)

| Param | Value |
|---|---|
| `prompt` | The `nano-banana-pro` hero-frame prompt for this shot, verbatim |
| `model` | `nano-banana-pro` — needed for the reasoning step and the type rendering |
| `aspectRatio` | `"16:9"` / `"9:16"` / `"1:1"` — MUST match the video call |
| `referenceImages` | Sheet URLs for this shot's assets, in slot order (first = @Image1). Omit when no assets |

Then `Unsora AI:wait_for_image` (`intervalSeconds: 5`, `maxAttempts: 60`). Keep
the returned image URL — pass it straight to `create_video` as `image`. Pull a
local copy: `curl --fail --location --retry 2 -o frames/shot_01.png "<IMAGE_URL>"`.

---

## 4. Unsora — clip (`create_video`)

| Param | Value |
|---|---|
| `prompt` | The `seedance-2.0` animation prompt for this shot, verbatim |
| `model` | `seedance-2.0` (not `-fast`; the prompts are written for full) |
| `image` | The hero-frame URL from `wait_for_image` (the start frame) |
| `aspectRatio` | **Identical** to the image call |
| `duration` | Integer seconds, rounded up to fit measured narration plus lead/tail. Inspect live minimum and maximum; if the current minimum is 4s, a 3s edit generates at 4s and is trimmed in post |
| `generateAudio` | `true` — the paper-foley bed is the clip's whole audio design |
| `referenceImages` | The SAME sheet URLs as this shot's hero frame, same order. Slot math: `image` = @Image1, so the first entry here = @Image2. Omit when no assets |
| `lastImage` | Omit (no cross-shot chaining) |

Then `Unsora AI:wait_for_video` (`generationId`, `intervalSeconds: 10`,
`maxAttempts: 90`). Generation latency varies; a wait timeout does not mean the remote job failed. `curl --fail --location --retry 2 -o clips/shot_01.mp4
"<VIDEO_URL>"`.

**Trim a 3s beat generated at 4s** (re-encode so the cut is exact):

```bash
ffmpeg -n -i clips/shot_03_raw.mp4 -t 3 -c:v libx264 -pix_fmt yuv420p -crf 18 \
  -c:a aac -b:a 192k clips/shot_03.mp4
```

When generation is requested and account limits are relevant, check available account tools without changing authorization: `Unsora AI:get_subscription`
(`isActive`), `Unsora AI:get_credits` (balance).

---

## 5. Unsora — music (`create_music`, optional)

| Param | Value |
|---|---|
| `prompt` | Editorial underscore brief — genre, mood, tempo, "instrumental, no vocals" (e.g. "restrained editorial underscore, light percussion, curious, no vocals") |
| `model` | `mureka-7.5` — the instrumental BGM model; omit `lyrics` |
| `output_format` | `"mp3"` |

Then `Unsora AI:wait_for_music` (`generationId`, `intervalSeconds: 5`,
`maxAttempts: 60`) → download to `music.mp3`. The bed is a fixed length that rarely
matches the film — loop (`-stream_loop -1`) or trim (`-t <dur>`) it in the mix and
fade the tail. The song models (`mureka-9/8/o2/7.6`, `auto`) require lyrics and add
vocals — never use them for a bed. Record `music.source: "unsora_create_music"`.

---

## 6. Voiceover — supplied file

The simplest route, and the one that always works. Unsora has no TTS, so if the
user has narration already — recorded themselves, or exported from a tool of their
own — take it as-is.

Ask for one file per beat (`vo/vo_01.mp3`, `vo/vo_02.mp3`, …) if they can split
it; otherwise take one continuous read and cut it against the beats:

```bash
# whole-file duration, then per-beat splits at the timestamps you mark up
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 vo/full.mp3
ffmpeg -n -i vo/full.mp3 -af "atrim=start=0:end=4.6,asetpts=PTS-STARTPTS" -ar 48000 -c:a pcm_s16le vo/vo_01.wav
ffmpeg -n -i vo/full.mp3 -af "atrim=start=4.6:end=9.2,asetpts=PTS-STARTPTS" -ar 48000 -c:a pcm_s16le vo/vo_02.wav
```

Listen at split boundaries and measure the decoded outputs; MP3 stream-copy cuts are packet-aligned and are unsuitable for exact narration boundaries.

Record `vo.mode: "supplied"` and the source path in the manifest.

---

## 7. Voiceover — session TTS tool

If the user wants the narration synthesized, use whatever TTS tool is **actually
connected in this session**. This skill deliberately names no provider — check
what's available at run time rather than assuming.

**Find one.** Search the session's tools for text-to-speech capability (terms like
`text_to_speech`, `tts`, `generate_audio`, `speech`, `voice`). If the client
defers tools, load the schema before calling. If nothing turns up, say so plainly
and fall back to §6 or the silent cut — never invent a provider, and never promise
a voice you can't produce.

**Then, whatever the tool is, the shape is the same:**

1. **List/audition voices** if the tool offers it, and pick ONE whose tone fits
   the film — editorial, measured, curious.
2. **One call per VO line** (one segment per shot). Pass the line as the text to
   speak; pass the same voice id every time so the narrator doesn't change
   mid-film.
3. **Retrieve the audio.** Some tools return a URL directly, some return a job or
   asset id you poll, some render into a widget with a download link. Get to a real
   URL, then pull it local: `curl --fail --location --retry 2 -o vo/vo_01.mp3 "<AUDIO_URL>"`.
4. **Sanity-check the first line** before synthesizing the rest — wrong voice
   across 20 lines is 20 wasted calls.

**Whatever the source:** never place a VO line inside an Unsora `create_video`
prompt — the narration is a separate track. After synthesis, `ffprobe` each line's
real duration and set each shot's `duration` to fit it (§10). Record the actual
source + voice in the manifest `vo` block; never say Unsora made the voice.

---

## 8. Manifest schema

Write `shots.json` at the end of planning, before any generation; update after every accepted job and verified result. Write a sibling temporary file and atomically replace the manifest, retaining the previous valid copy. Record each generation ID before polling. The following example is a single pending shot; it is not ready for assembly.

```json
{
  "project": "vox-explainer",
  "aspect_ratio": "16:9",
  "accent": "vox yellow",
  "palette": { "ground": "off-white newsprint", "subjects": "muted near-B&W cut-outs", "accent": "yellow" },
  "vo": { "mode": "supplied", "tool": "<the TTS tool actually used, or null>", "voice_id": "…", "supplied_file": null },
  "music": { "source": "none", "file": null, "id": null },
  "brand_bug": null,
  "total_seconds": 6,
  "assets": [
    { "name": "founder", "kind": "character", "used_in_shots": [2,5,7],
      "sheet_prompt": "…", "generation_id": null, "sheet_url": null,
      "sheet_path": null, "status": "pending" }
  ],
  "shots": [
    { "n": 1, "point": "the border moved 200 miles",
      "card": "200 MILES", "subject": "torn map with redline",
      "accent_use": "redline + card", "assets": [],
      "vo_line": "In 1848 the line jumped two hundred miles west — overnight.",
      "vo_file": "vo/vo_01.mp3", "vo_dur": 4.6, "seconds": 6, "generation_seconds": 6, "lead_ms": 300, "tail_ms": 300,
      "nb_prompt": "…", "seedance_prompt": "…",
      "image_generation_id": null, "image_url": null,
      "video_generation_id": null, "video_url": null,
      "clip_path": null, "offset_ms": 300, "status": "pending" }
  ]
}
```

Shot `status`: `pending` → `vo_done` → `image_queued` → `image_done` →
`video_queued` → `done` (or `failed` + `error`). Asset `status`: `pending` →
`queued` → `done`/`failed`. No shot listing an asset generates until that asset is
`done`; on resume, check assets first. `vo_dur` is measured narration duration; `seconds` is the final edit window; `generation_seconds` is the model request duration; `offset_ms` is absolute narration start in the final film. Recompute offsets from the cumulative preceding edit windows plus `lead_ms`. A silent shot can go from pending directly to image_queued. A done asset must still exist and decode.

---

## 9. ffmpeg — concat

Inspect and normalize every clip to the same codec, dimensions, frame rate, time base, pixel format and audio layout. The same model and aspect ratio do not guarantee matching streams. Trim raw clips to their final edit windows and add silent audio when a clip has no foley, or use a separately planned audio-free pipeline.

Use manifest array order. Never glob `shot_*.mp4`: that can include raw, rejected or duplicate clips. Generate the list only after every listed shot is done and verified:

```bash
python3 /path/to/skill/scripts/prepare_timeline.py shots.json --probe --output-dir assembly-01
ffmpeg -n -f concat -safe 0 -i assembly-01/concat_list.txt -c copy cut.mp4
```

The helper checks unique shot IDs, local nonempty files, narration windows, stale offsets, clip duration and total duration. Without `--probe`, it trusts declared durations and explicitly reports that media was not probed. It does not validate stream compatibility or visual quality. Use a new output directory after repairs; it never replaces earlier output.

If stream copy fails, normalize each source first. Re-encoding a concat-demuxer input alone does not repair incompatible source dimensions or time bases.

---

## 10. ffmpeg — VO timing + duck/mix

Each shot was sized to its VO line in Phase 4, so each `vo_NN` fits its window;
placement is the cumulative preceding edit windows plus that shot's chosen lead. First normalize the explicit voice files listed in the manifest (including WAV, MP3 or MP4 inputs) so ducking is predictable. Use distinct outputs and remeasure them:

```bash
ffmpeg -n -i vo/vo_01.wav -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 vo/vo_01_n.wav
```

If a line came back slightly longer than its window, speed it pitch-safe (keep
`atempo` in `[1.0, 1.15]`) before placing only if the user accepts the pacing change. Otherwise resize/split the edit without truncating speech; prefer local holds or trims within approved scope before paid regeneration:

```bash
ffmpeg -n -i vo/vo_03_n.wav -filter:a "atempo=1.10" vo/vo_03_fit.wav
```

**Mix** — VO on top, music bed ducked under the VO (sidechain), clip foley low.
Offsets in ms are each shot's start (`offset_ms` in the manifest):

```bash
# example only: 20-second picture, VO starts at 0.2 / 5.4 / 10.1 / 15.0 s
# Replace offsets and 20 with the validated timeline; no input may overrun its window.
ffmpeg -n -i cut.mp4 -stream_loop -1 -i music.mp3 \
  -i vo/vo_01_n.wav -i vo/vo_02_n.wav -i vo/vo_03_fit.wav -i vo/vo_04_n.wav \
  -filter_complex "\
    [2:a]adelay=200|200[a1];[3:a]adelay=5400|5400[a2];\
    [4:a]adelay=10100|10100[a3];[5:a]adelay=15000|15000[a4];\
    [a1][a2][a3][a4]amix=inputs=4:normalize=0,apad,atrim=duration=20,asplit=2[vo_key][vo_mix];\
    [1:a]volume=0.5,atrim=duration=20[mus];\
    [mus][vo_key]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[musd];\
    [0:a]volume=0.22,apad,atrim=duration=20[foley];\
    [foley][musd][vo_mix]amix=inputs=3:duration=longest:normalize=0,atrim=duration=20[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k -t 20 -movflags +faststart final.mp4
```

`asplit` is required: the narration feeds two consumers, sidechain detection and audible output. Here `normalize=0` keeps deliberate input gains; the sum can clip, so measure the final mix and adjust gains/limiting before delivery. Normalized mixing is a valid alternative with a different gain plan. Tuning: raise `[1:a]volume` for a louder bed; lower `ratio`/`threshold` for
gentler ducking; raise `[0:a]volume` if the paper foley should read more; keep VO
at unity so it always sits on top. **No music bed** → omit music and sidechain stages, omit the unnecessary `asplit`, and mix padded foley plus narration to the exact picture duration. **No foley stream** → supply `anullsrc=r=48000:cl=stereo` or omit foley and rebuild the graph; never reference a nonexistent `[0:a]`. **No narration** → omit narration and sidechain stages. **Fully silent film** → `ffmpeg -n -i cut.mp4 -map 0:v:0 -c:v copy -an final.mp4`. “No narration” can still include approved foley/music; do not confuse it with fully silent.

---

## 11. ffmpeg — brand-bug overlay (optional, user-supplied logo only)

Never bake a brand into a Nano Banana prompt (it drifts/warps) — overlay it in
post. Persistent corner bug (transparent `logo.png`):

```bash
ffmpeg -n -i final.mp4 -i logo.png \
  -filter_complex "[1:v]scale=iw*0.10:-1[lg];[0:v][lg]overlay=W-w-40:H-h-40:format=auto[v]" \
  -map "[v]" -map 0:a? -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a copy -movflags +faststart final-branded.mp4
```

---

Keep `final.mp4` as the unbranded original. Verify `final-branded.mp4` before selecting it for delivery.

## 12. Verification

Run before presenting. A concat that drops a clip yields a valid file that is just
short, with no warning.

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of default=nw=1 final.mp4
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,channels -of default=nw=1 final.mp4
```

Duration tolerance ±0.5s vs the manifest's `total_seconds`. Larger → a clip came
back the wrong length; check per-clip with `ffprobe`.

---

## 13. Resume after failure

Read the last valid manifest and verify retained assets before any new calls.
- `vo_done`: reuse audio; proceed to the image stage.
- `image_queued` or `video_queued` with an ID: query/wait for that same ID. A timeout is unknown completion, not permission to submit a duplicate paid job.
- `image_done`: reuse the image and proceed to the video stage.
- `done` with a missing local file: recover/download the existing result by ID or URL first.
- `failed`: inspect the provider's actual terminal error. Authentication or exhausted credits require resolution, and content rejection needs a prompt review. Bound retries within the user's approved spend.

Preserve successful stages and all original files. If status cannot be reconciled, explain the uncertainty before a chargeable resubmission. Recheck timeline and final duration after any repair.

---

## 14. Optional posting (Unsora)

Publishing needs explicit authorization identifying the final media, caption, account and schedule. Prepare these before the final publishing action; generation approval alone does not authorize posting. Honor publication authority already given for those exact details.

1. `Unsora AI:get_subscription` → confirm `isActive` (posting needs a paid plan).
2. `Unsora AI:get_accounts` → list connected Instagram / TikTok accounts.
3. Unsora needs a reachable `mediaUrl` — a local MP4 won't do. If there's no public
   URL, say so and ask how they want to host it.
4. `Unsora AI:create_post` with `accountIds`, `caption`, `mediaType: "video"`,
   `mediaUrl`, optional `scheduled_at` (ISO; omit to post now).
5. Confirm with `Unsora AI:list_posts`; distinguish queued, scheduled, failed and published states. Do not treat a successful create request as proof that a post is live.
