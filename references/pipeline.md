# Pipeline reference — Unsora generation · VO · ffmpeg

Exact mechanics for Phases 4–8. The defining split: **all image/video/music
generation is Unsora through Unsora MCP**; **the voiceover comes from outside
Unsora** (it has no TTS) — either a file the user supplies or whatever TTS tool is
connected in the session; **assembly and mix are ffmpeg**. The user opted into the
VO source at the front door, so act on that choice directly; if a call returns an
auth error, surface it and the user re-authenticates.

This skill assumes it is running in Claude, OpenClaw, or Hermes Agent with Unsora
MCP connected. If Unsora MCP is unavailable, do not start generation planning.

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

Copy only `final.mp4` to the outputs directory.

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
`curl -L -o sheets/<name>.png "<URL>"`. Show each sheet to the user before shots.

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
local copy: `curl -L -o frames/shot_01.png "<IMAGE_URL>"`.

---

## 4. Unsora — clip (`create_video`)

| Param | Value |
|---|---|
| `prompt` | The `seedance-2.0` animation prompt for this shot, verbatim |
| `model` | `seedance-2.0` (not `-fast`; the prompts are written for full) |
| `image` | The hero-frame URL from `wait_for_image` (the start frame) |
| `aspectRatio` | **Identical** to the image call |
| `duration` | Integer seconds. Set to the shot's VO-line length (Phase 4). Seedance floor is 4s — a planned 3s beat generates at 4 and is trimmed in post |
| `generateAudio` | `true` — the paper-foley bed is the clip's whole audio design |
| `referenceImages` | The SAME sheet URLs as this shot's hero frame, same order. Slot math: `image` = @Image1, so the first entry here = @Image2. Omit when no assets |
| `lastImage` | Omit (no cross-shot chaining) |

Then `Unsora AI:wait_for_video` (`generationId`, `intervalSeconds: 10`,
`maxAttempts: 90`). Seedance 2.0 runs ~7 min/clip. `curl -L -o clips/shot_01.mp4
"<VIDEO_URL>"`.

**Trim a 3s beat generated at 4s** (re-encode so the cut is exact):

```bash
ffmpeg -y -i clips/shot_03_raw.mp4 -t 3 -c:v libx264 -pix_fmt yuv420p -crf 18 \
  -c:a aac -b:a 192k clips/shot_03.mp4
```

Pre-flight only when diagnosing a rejection: `Unsora AI:get_subscription`
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
ffmpeg -y -i vo/full.mp3 -ss 0     -to 4.6  -c copy vo/vo_01.mp3
ffmpeg -y -i vo/full.mp3 -ss 4.6   -to 9.2  -c copy vo/vo_02.mp3
```

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
   URL, then pull it local: `curl -L -o vo/vo_01.mp3 "<AUDIO_URL>"`.
4. **Sanity-check the first line** before synthesizing the rest — wrong voice
   across 20 lines is 20 wasted calls.

**Whatever the source:** never place a VO line inside an Unsora `create_video`
prompt — the narration is a separate track. After synthesis, `ffprobe` each line's
real duration and set each shot's `duration` to fit it (§10). Record the actual
source + voice in the manifest `vo` block; never say Unsora made the voice.

---

## 8. Manifest schema

Write `shots.json` at the end of Phase 3, before any generation; update after
every step. This is what makes a long run resumable.

```json
{
  "project": "vox-explainer",
  "aspect_ratio": "16:9",
  "accent": "vox yellow",
  "palette": { "ground": "off-white newsprint", "subjects": "muted near-B&W cut-outs", "accent": "yellow" },
  "vo": { "mode": "generated | supplied | none", "tool": "<the TTS tool actually used, or null>", "voice_id": "…", "supplied_file": null },
  "music": { "source": "unsora_create_music | supplied | none", "file": "music.mp3", "id": null },
  "brand_bug": null,
  "total_seconds": 62,
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
      "vo_file": "vo/vo_01.mp3", "vo_dur": 4.6, "seconds": 5,
      "nb_prompt": "…", "seedance_prompt": "…",
      "image_generation_id": null, "image_url": null,
      "video_generation_id": null, "video_url": null,
      "clip_path": null, "offset_ms": 200, "status": "pending" }
  ]
}
```

Shot `status`: `pending` → `vo_done` → `image_queued` → `image_done` →
`video_queued` → `done` (or `failed` + `error`). Asset `status`: `pending` →
`queued` → `done`/`failed`. No shot listing an asset generates until that asset is
`done`; on resume, check assets first. `vo_dur`/`seconds`/`offset_ms` are what §10
fills.

---

## 9. ffmpeg — concat

Clips share codec/resolution/fps (same model + ratio), so stream copy works. Order
from the manifest, not a directory listing; zero-pad shot numbers so a glob sorts
right (`shot_01`, not `shot_1`).

```bash
cd <agent-workspace>/vox-collage
: > concat_list.txt
for f in clips/shot_*.mp4; do printf "file '%s'\n" "$f" >> concat_list.txt; done
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy cut.mp4
```

Fallback if `-c copy` errors on a mismatch (e.g. mixed trimmed clips):

```bash
ffmpeg -y -f concat -safe 0 -i concat_list.txt \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a aac -b:a 192k -movflags +faststart cut.mp4
```

---

## 10. ffmpeg — VO timing + duck/mix

Each shot was sized to its VO line in Phase 4, so each `vo_NN` fits its window;
placement is each shot's cumulative start offset (a small ~0.2s lead). First
normalise every VO line so the duck is predictable:

```bash
for f in vo/vo_*.mp3; do
  ffmpeg -y -i "$f" -af loudnorm=I=-16:TP=-1.5:LRA=11 -ar 48000 "${f%.mp3}_n.wav"; done
```

If a line came back slightly longer than its window, speed it pitch-safe (keep
`atempo` in `[1.0, 1.15]`) before placing — don't stretch video:

```bash
ffmpeg -y -i vo/vo_03_n.wav -filter:a "atempo=1.10" vo/vo_03_fit.wav
```

**Mix** — VO on top, music bed ducked under the VO (sidechain), clip foley low.
Offsets in ms are each shot's start (`offset_ms` in the manifest):

```bash
# example: 4 shots, VO at 0.2 / 5.4 / 10.1 / 15.0 s; music looped; -shortest to picture
ffmpeg -y -i cut.mp4 -stream_loop -1 -i music.mp3 \
  -i vo/vo_01_n.wav -i vo/vo_02_n.wav -i vo/vo_03_fit.wav -i vo/vo_04_n.wav \
  -filter_complex "\
    [2:a]adelay=200|200[a1];[3:a]adelay=5400|5400[a2];\
    [4:a]adelay=10100|10100[a3];[5:a]adelay=15000|15000[a4];\
    [a1][a2][a3][a4]amix=inputs=4:normalize=0[vo];\
    [1:a]volume=0.5[mus];\
    [mus][vo]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[musd];\
    [0:a]volume=0.22[foley];\
    [foley][musd][vo]amix=inputs=3:duration=first:normalize=0[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

`normalize=0` is not optional (without it `amix` divides by input count and drops
6 dB). Tuning: raise `[1:a]volume` for a louder bed; lower `ratio`/`threshold` for
gentler ducking; raise `[0:a]volume` if the paper foley should read more; keep VO
at unity so it always sits on top. **No music bed** → drop the music input and the
`[mus]/[musd]` lines, mix `[foley]` + `[vo]` only. **Silent film** → `cp cut.mp4
final.mp4`.

---

## 11. ffmpeg — brand-bug overlay (optional, user-supplied logo only)

Never bake a brand into a Nano Banana prompt (it drifts/warps) — overlay it in
post. Persistent corner bug (transparent `logo.png`):

```bash
ffmpeg -y -i final.mp4 -i logo.png \
  -filter_complex "[1:v]scale=iw*0.10:-1[lg];[0:v][lg]overlay=W-w-40:H-h-40:format=auto[v]" \
  -map "[v]" -map 0:a -c:v libx264 -pix_fmt yuv420p -crf 18 -c:a copy -movflags +faststart b.mp4 \
  && mv b.mp4 final.mp4
```

---

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

Read `shots.json`. Regenerate only shots whose `status` ≠ `done`.
- `vo_done` → skip TTS, start at `create_image`.
- `image_queued` with an id → `wait_for_image` again (job may be alive).
- `image_done` → skip to `create_video`.
- `failed` → read the error. A content rejection needs a prompt edit, not a retry;
  a timeout needs a retry.

Never regenerate a `done` shot "for consistency" — each shot is independent and a
re-roll comes back different. Re-verify total duration after any repair.

---

## 14. Optional posting (Unsora)

Publishing needs its own explicit yes, separate from the yes to generate.

1. `Unsora AI:get_subscription` → confirm `isActive` (posting needs a paid plan).
2. `Unsora AI:get_accounts` → list connected Instagram / TikTok accounts.
3. Unsora needs a reachable `mediaUrl` — a local MP4 won't do. If there's no public
   URL, say so and ask how they want to host it.
4. `Unsora AI:create_post` with `accountIds`, `caption`, `mediaType: "video"`,
   `mediaUrl`, optional `scheduled_at` (ISO; omit to post now).
5. Confirm with `Unsora AI:list_posts`. Draft the caption; let the user edit before
   it goes out.
