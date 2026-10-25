#!/usr/bin/env python3
"""Validate an existing cut manifest and emit an ordered FFmpeg concat list.

No network access, generation, media editing, or source-manifest writes.
"""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys


def number(value, label, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    if not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError(f"{label} must be {'positive' if positive else 'nonnegative'} and finite")
    return value


def local_file(root, value, label):
    if not isinstance(value, str) or not value or any(c in value for c in "\0\r\n\\"):
        raise ValueError(f"{label} must be a local relative path")
    candidate = (root / value).resolve()
    if Path(value).is_absolute() or not candidate.is_relative_to(root):
        raise ValueError(f"{label} escapes the project directory")
    if not candidate.is_file() or candidate.stat().st_size == 0:
        raise ValueError(f"{label} is missing or empty: {value}")
    return candidate


def probe_duration(file, executable):
    result = subprocess.run(
        [executable, "-v", "error", "-show_entries", "format=duration", "-of", "json", str(file)],
        capture_output=True, text=True, check=True, timeout=30,
    )
    value = float(json.loads(result.stdout)["format"]["duration"])
    return number(value, f"duration of {file.name}", positive=True)


def prepare(manifest, root, probe=None):
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object")
    shots = manifest.get("shots")
    if not isinstance(shots, list) or not shots:
        raise ValueError("Manifest needs a nonempty shots array")
    root = Path(root).resolve()
    voice = manifest.get("vo")
    mode = voice.get("mode") if isinstance(voice, dict) else None
    if mode not in {"generated", "supplied", "none"}:
        raise ValueError("vo.mode must be generated, supplied, or none")
    timeline, files, seen = [], [], set()
    elapsed = 0.0
    for shot in shots:
        if not isinstance(shot, dict):
            raise ValueError("Each shot must be an object")
        n = shot.get("n")
        if isinstance(n, bool) or not isinstance(n, int) or n < 1 or n in seen:
            raise ValueError("Shot numbers must be positive unique integers")
        seen.add(n)
        if shot.get("status") != "done":
            raise ValueError(f"Shot {n} is not done; do not silently omit it")
        duration = number(shot.get("seconds"), f"Shot {n} seconds", positive=True)
        clip = local_file(root, shot.get("clip_path"), f"Shot {n} clip_path")
        if probe and abs(probe(clip) - duration) > 0.1:
            raise ValueError(f"Shot {n} clip duration differs from its edit window; trim or normalize before assembly")
        row = {"n": n, "start_seconds": round(elapsed, 6), "seconds": duration, "clip_path": str(clip)}
        if mode != "none":
            audio = local_file(root, shot.get("vo_file"), f"Shot {n} vo_file")
            voice_duration = probe(audio) if probe else number(shot.get("vo_dur"), f"Shot {n} vo_dur", positive=True)
            lead = number(shot.get("lead_ms", 300), f"Shot {n} lead_ms") / 1000
            tail = number(shot.get("tail_ms", 300), f"Shot {n} tail_ms") / 1000
            if lead + voice_duration + tail > duration + 0.001:
                raise ValueError(f"Shot {n} narration does not fit with its lead and tail; resize the edit before generation")
            offset = round((elapsed + lead) * 1000)
            if "offset_ms" in shot and abs(number(shot["offset_ms"], f"Shot {n} offset_ms") - offset) > 1:
                raise ValueError(f"Shot {n} offset_ms is stale; expected {offset}")
            row.update(vo_file=str(audio), vo_dur=voice_duration, offset_ms=offset)
        files.append(clip)
        timeline.append(row)
        elapsed += duration
    expected = number(manifest.get("total_seconds"), "total_seconds", positive=True)
    if abs(expected - elapsed) > 0.001:
        raise ValueError(f"total_seconds {expected} does not equal shot sum {elapsed:g}")
    # FFconcat uses its own single-quote escaping; this is not a shell command.
    quoted = ["file '" + file.as_posix().replace("'", "'\\''") + "'" for file in files]
    return {"total_seconds": round(elapsed, 6), "shots": timeline}, "ffconcat version 1.0\n" + "\n".join(quoted) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True, help="New directory for timeline.json and concat_list.txt")
    parser.add_argument("--probe", action="store_true", help="Measure actual clip and voiceover durations with ffprobe")
    parser.add_argument("--ffprobe", default="ffprobe")
    args = parser.parse_args()
    try:
        source = args.manifest.resolve()
        manifest = json.loads(source.read_text(encoding="utf-8"))
        probe = (lambda file: probe_duration(file, args.ffprobe)) if args.probe else None
        timeline, concat = prepare(manifest, source.parent, probe)
        # Refuse any existing directory, including prior successful output.
        args.output_dir.mkdir(parents=True, exist_ok=False)
        (args.output_dir / "timeline.json").write_text(json.dumps(timeline, indent=2) + "\n", encoding="utf-8")
        (args.output_dir / "concat_list.txt").write_text(concat, encoding="utf-8")
        print(f"Validated {len(timeline['shots'])} shots; {timeline['total_seconds']:g}s. Media durations {'probed' if probe else 'not probed'}.")
        return 0
    except (ValueError, OSError, subprocess.SubprocessError, KeyError, TypeError) as error:
        print(f"Timeline validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
