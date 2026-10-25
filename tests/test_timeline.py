import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "prepare_timeline.py"
spec = importlib.util.spec_from_file_location("timeline", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in ["first's clip.mp4", "second.mp4", "first.wav", "second.wav"]:
            (self.root / name).write_bytes(b"synthetic")
        self.manifest = {"vo": {"mode": "supplied"}, "total_seconds": 12, "shots": [
            {"n": 9, "status": "done", "seconds": 6, "clip_path": "first's clip.mp4", "vo_file": "first.wav", "vo_dur": 5.4},
            {"n": 2, "status": "done", "seconds": 6, "clip_path": "second.mp4", "vo_file": "second.wav", "vo_dur": 4.6},
        ]}

    def test_manifest_order_offsets_and_quoted_names(self):
        plan, concat = module.prepare(self.manifest, self.root)
        self.assertEqual([s["n"] for s in plan["shots"]], [9, 2])
        self.assertEqual([s["offset_ms"] for s in plan["shots"]], [300, 6300])
        self.assertLess(concat.index("first"), concat.index("second"))
        self.assertIn("first'\\''s clip.mp4", concat)

    def test_narration_must_fit_including_both_margins(self):
        self.manifest["shots"][0]["vo_dur"] = 5.5
        with self.assertRaisesRegex(ValueError, "does not fit"):
            module.prepare(self.manifest, self.root)

    def test_invalid_manifests_fail_without_skipping_shots(self):
        for key, value in [("status", "video_queued"), ("seconds", 0), ("seconds", float("nan")),
                           ("seconds", True), ("vo_dur", float("inf")), ("offset_ms", 200),
                           ("clip_path", "missing.mp4"), ("clip_path", "../outside.mp4"),
                           ("clip_path", "bad\nfile.mp4"), ("n", True), ("n", 2)]:
            with self.subTest(key=key, value=value):
                manifest = copy.deepcopy(self.manifest)
                manifest["shots"][0][key] = value
                with self.assertRaises(ValueError):
                    module.prepare(manifest, self.root)

    def test_total_must_match_actual_edit_windows(self):
        self.manifest["total_seconds"] = 13
        with self.assertRaisesRegex(ValueError, "shot sum"):
            module.prepare(self.manifest, self.root)

    def test_voice_mode_must_be_an_object(self):
        for value in [None, [], "none", True]:
            self.manifest["vo"] = value
            with self.assertRaisesRegex(ValueError, "vo.mode"):
                module.prepare(self.manifest, self.root)

    def test_empty_clip_is_not_a_finished_asset(self):
        (self.root / "second.mp4").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "missing or empty"):
            module.prepare(self.manifest, self.root)

    def test_symlink_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "clip.mp4"
            target.write_bytes(b"outside")
            (self.root / "link.mp4").symlink_to(target)
            self.manifest["shots"][0]["clip_path"] = "link.mp4"
            with self.assertRaisesRegex(ValueError, "escapes"):
                module.prepare(self.manifest, self.root)

    def test_silent_cut_needs_no_voice_assets(self):
        self.manifest["vo"]["mode"] = "none"
        for shot in self.manifest["shots"]:
            del shot["vo_file"]
            del shot["vo_dur"]
        plan, _ = module.prepare(self.manifest, self.root)
        self.assertNotIn("offset_ms", plan["shots"][0])

    def test_probe_uses_measured_voice_duration(self):
        def probe(file):
            return 5.5 if file.suffix == ".wav" else 6
        with self.assertRaisesRegex(ValueError, "does not fit"):
            module.prepare(self.manifest, self.root, probe)

    def test_probe_detects_truncated_clip(self):
        with self.assertRaisesRegex(ValueError, "clip duration"):
            module.prepare(self.manifest, self.root, lambda _: 2)

    def test_cli_preserves_manifest_and_previous_output(self):
        source = self.root / "shots.json"
        original = json.dumps(self.manifest).encode()
        source.write_bytes(original)
        output = self.root / "assembly"
        command = [sys.executable, str(SCRIPT), str(source), "--output-dir", str(output)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertIn("not probed", first.stdout)
        saved = (output / "timeline.json").read_bytes()
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual((output / "timeline.json").read_bytes(), saved)
        self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
