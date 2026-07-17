# Vox Style Collage Video

Agent skill for turning scripts, beat lists, or fact lists into Vox-style
paper-collage explainer videos.

This skill is intended for **Claude**, **OpenClaw**, and **Hermes Agent** style
skill runtimes. It is built around the **Unsora MCP** toolset from
[Unsora](https://tryunsora.com/), which is required for image, video, music
generation, and optional social posting.

## Prerequisites

- A compatible agent runtime: Claude, OpenClaw, or Hermes Agent
- Unsora MCP connected and authenticated from [tryunsora.com](https://tryunsora.com/)
- Available Unsora credits for image, video, and optional music generation
- `ffmpeg` and `ffprobe` available locally for assembly, timing, and mixing
- A voiceover source, either supplied audio or a separate session TTS tool

Unsora is deliberately **not** used for narration because Unsora has no TTS. The
voiceover must come from a supplied audio file or another TTS tool connected to
the session.

## What It Does

The skill defines a narration-first production workflow using:

- Unsora MCP image generation for hero frames and reference sheets
- Unsora MCP video generation for limited-frame cutout animation
- Unsora MCP music generation for editorial underscoring
- External voiceover or session TTS for narration
- ffmpeg for timing, assembly, and final mix

## Contents

- `SKILL.md` - main skill instructions and workflow
- `references/style-dna.md` - visual system, prompt templates, and style checks
- `references/pipeline.md` - generation, voiceover, ffmpeg, and delivery pipeline
- `references/beat-mapping.md` - narration segmentation and shot mapping

## Usage

Install or copy this folder into your agent's skills directory, then invoke it
for Vox-style, editorial collage, or paper-collage explainer video work.

Before using it, confirm that Unsora MCP exposes the required tools:

- `create_image` / `wait_for_image`
- `create_video` / `wait_for_video`
- `create_music` / `wait_for_music`
- Optional: `get_subscription`, `get_credits`, `create_post`, `list_posts`
