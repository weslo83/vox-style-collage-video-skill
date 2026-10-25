"""Exercise the documented commands with local, disposable media."""
import importlib.util
import io
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
import wave

ROOT = Path(__file__).resolve().parents[1]
FFMPEG = os.environ.get("FFMPEG_BINARY") or shutil.which("ffmpeg")
spec = importlib.util.spec_from_file_location("timeline", ROOT / "scripts/prepare_timeline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@unittest.skipUnless(FFMPEG, "FFmpeg is required for media integration tests")
class MediaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def ffmpeg(self, *args):
        result = subprocess.run([FFMPEG, "-v", "error", "-nostdin", *args], cwd=self.root,
                                capture_output=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        return result.stdout

    def clip(self, name, color, seconds=1, audio=False):
        args = ["-f", "lavfi", "-i", f"color=c={color}:s=16x16:r=25:d={seconds}"]
        if audio:
            # Deliberately shorter than the picture: the mix must not truncate it.
            args += ["-f", "lavfi", "-i", "sine=frequency=200:sample_rate=48000:duration=0.1"]
        self.ffmpeg(*args, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", name)

    def test_concat_uses_manifest_order_and_escapes_apostrophes(self):
        self.clip("first's clip.mp4", "red")
        self.clip("second.mp4", "blue")
        self.clip("shot_rejected.mp4", "green")
        manifest = {"vo": {"mode": "none"}, "total_seconds": 2, "shots": [
            {"n": 9, "status": "done", "seconds": 1, "clip_path": "first's clip.mp4"},
            {"n": 2, "status": "done", "seconds": 1, "clip_path": "second.mp4"},
        ]}
        _, concat = module.prepare(manifest, self.root)
        (self.root / "concat.txt").write_text(concat)
        self.ffmpeg("-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "cut.mp4")
        pixels = self.ffmpeg("-i", "cut.mp4", "-map", "0:v", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1")
        self.assertEqual(len(pixels), 50 * 16 * 16 * 3)
        self.assertGreater(pixels[0], 240)  # first frame red
        self.assertLess(pixels[2], 10)
        self.assertGreater(pixels[-1], 240)  # last frame blue
        self.assertLess(pixels[-3], 10)

    def test_documented_mix_keeps_full_picture_and_audio(self):
        self.clip("cut.mp4", "white", seconds=20, audio=True)
        self.ffmpeg("-f", "lavfi", "-i", "sine=frequency=400:sample_rate=48000:duration=0.5", "music.mp3")
        (self.root / "vo").mkdir()
        for name in ["vo_01_n.wav", "vo_02_n.wav", "vo_03_fit.wav", "vo_04_n.wav"]:
            self.ffmpeg("-f", "lavfi", "-i", "sine=frequency=800:sample_rate=48000:duration=0.6", f"vo/{name}")
        blocks = re.findall(r"```bash\n(.*?)```", (ROOT / "references/pipeline.md").read_text(), re.S)
        graph = next(block for block in blocks if "sidechaincompress=" in block)
        command = "\n".join(line for line in graph.splitlines() if not line.startswith("#"))
        args = shlex.split(command.replace("\\\n", ""))
        self.assertEqual(args.pop(0), "ffmpeg")
        self.ffmpeg(*args)
        pcm = self.ffmpeg("-i", "final.mp4", "-vn", "-c:a", "pcm_s16le", "-f", "wav", "pipe:1")
        with wave.open(io.BytesIO(pcm)) as audio:
            frames = audio.readframes(audio.getnframes())
            seconds = len(frames) / (audio.getframerate() * audio.getnchannels() * audio.getsampwidth())
        self.assertGreaterEqual(seconds, 19.95)
        self.assertLess(seconds, 20.1)
        pixels = self.ffmpeg("-i", "final.mp4", "-map", "0:v", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1")
        self.assertEqual(len(pixels), 500 * 16 * 16 * 3)


if __name__ == "__main__":
    unittest.main()
