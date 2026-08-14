import asyncio
import base64
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

from vidlens.media import find_media_files
import vidlens


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "scripts" / "vidlens.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("vidlens_runtime_boundary_test", RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self, payload=b"", content_type="image/png"):
        self._payload = payload
        self.headers = {"Content-Type": content_type}

    def read(self, size=-1):
        return self._payload if size < 0 else self._payload[:size]

    def close(self):
        pass


class MediaDiscoveryTests(unittest.TestCase):
    def test_package_version_is_2_1_0(self):
        self.assertEqual(vidlens.__version__, "2.1.0")

    def test_search_skips_dependency_directories_and_sorts_images_first(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            image = root / "latest.png"
            video = root / "older.mp4"
            ignored = root / "node_modules" / "ignored.png"
            ignored.parent.mkdir()
            image.write_bytes(b"image")
            time.sleep(0.01)
            video.write_bytes(b"video")
            ignored.write_bytes(b"ignored")
            result = find_media_files(str(root), max_results=10)
            names = [Path(item).name for item in result]
            self.assertEqual(names, ["latest.png", "older.mp4"])

    def test_keyword_matches_stem_and_limits_results(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("chart-1.png", "chart-2.png", "other.png"):
                (root / name).write_bytes(b"image")
            result = find_media_files(str(root), keyword="CHART", max_results=1)
            self.assertEqual(len(result), 1)
            self.assertIn("chart", Path(result[0]).name)


class RuntimeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime()

    def test_cli_positional_args_separate_media_from_question(self):
        media, task = self.runtime.separate_media_and_task(
            ["chart.png", "Does", "this", "show", "three", "bars?"], "")
        self.assertEqual(media, ["chart.png"])
        self.assertEqual(task, "Does this show three bars?")

    def test_url_download_uses_content_type_and_size_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            response = FakeResponse(b"png-data", "image/jpeg")
            with mock.patch.object(self.runtime.urllib.request, "urlopen", return_value=response):
                path, kind = self.runtime._download_url(
                    "https://example.test/photo?size=large", Path(temporary), 1)
            self.assertEqual(kind, "image")
            self.assertEqual(path.read_bytes(), b"png-data")
            self.assertEqual(path.suffix, ".jpg")

            oversize = FakeResponse(b"x" * (self.runtime.MAX_DOWNLOAD_BYTES + 1))
            with mock.patch.object(self.runtime.urllib.request, "urlopen", return_value=oversize):
                with self.assertRaisesRegex(RuntimeError, "too large"):
                    self.runtime._download_url(
                        "https://example.test/photo?size=large", Path(temporary), 2)

    def test_environment_overrides_primary_and_fallback_providers(self):
        values = {
            "VIDLENS_API_URL": "https://primary.test/v1",
            "VIDLENS_API_KEY": "primary-key",
            "VIDLENS_MODEL": "primary-model",
            "VIDLENS_FALLBACK1_URL": "https://fallback.test/v1",
            "VIDLENS_FALLBACK1_KEY": "fallback-key",
            "VIDLENS_FALLBACK1_MODEL": "fallback-model",
        }
        with mock.patch.dict(os.environ, values, clear=False):
            chain = self.runtime.build_provider_chain(self.runtime.load_config())
        self.assertEqual(chain, [
            ("https://primary.test/v1", "primary-key", "primary-model"),
            ("https://fallback.test/v1", "fallback-key", "fallback-model"),
        ])

    def test_total_deadline_clamps_provider_timeout(self):
        cfg = {"http_timeout": 90, "total_timeout": 7}
        provider = ("https://provider.test/v1", "key", "model")
        with mock.patch.object(self.runtime, "build_provider_chain", return_value=[provider]):
            with mock.patch.object(
                self.runtime,
                "_call_one_provider",
                return_value="ok",
            ) as call:
                result = self.runtime.analyze_image(
                    cfg, Path("image.png"), "image", "prompt")
        self.assertEqual(result, "ok")
        self.assertLessEqual(call.call_args.kwargs["timeout"], 7)

    def test_outbound_request_is_text_plus_image_and_returns_plain_text(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "marker.png"
            source.write_bytes(b"image-bytes")
            encoded = base64.b64encode(b"image-bytes").decode("ascii")
            response = FakeResponse(json.dumps({
                "choices": [{"message": {"content": "VLM-BOUNDARY-2468"}}]
            }).encode(), "application/json")
            requests = []

            def capture(request, timeout=None):
                requests.append((request, timeout))
                return response

            cfg = {
                "response_tokens": 1200,
                "verification_tokens": 350,
                "sampling_temp": 0.1,
                "http_timeout": 45,
            }
            with mock.patch.object(self.runtime.urllib.request, "urlopen", side_effect=capture):
                result = self.runtime._call_one_provider(
                    "https://vision.test/v1", "key", "vision-model", source,
                    "image", "VERDICT: PASS\nNEXT FIX: none", cfg, timeout=12)
            self.assertEqual(result, "VLM-BOUNDARY-2468")
            request, timeout = requests[0]
            self.assertEqual(timeout, 12)
            payload = json.loads(request.data.decode("utf-8"))
            content = payload["messages"][0]["content"]
            self.assertEqual(content[0], {"type": "text", "text": "VERDICT: PASS\nNEXT FIX: none"})
            self.assertEqual(content[1]["type"], "image_url")
            self.assertEqual(
                content[1]["image_url"]["url"],
                "data:image/png;base64," + encoded)
            self.assertEqual(payload["max_tokens"], 350)

    def test_agents_rule_defines_direct_image_boundary(self):
        rule = self.runtime.AGENTS_RULE
        self.assertIn("First confirm actual model/provider capability", rule)
        self.assertIn("path or URL is TEXT", rule)
        self.assertIn("generic image-view tool", rule)
        self.assertIn("do not retry it", rule)


class AsyncRuntimeTests(unittest.TestCase):
    def test_mcp_search_runs_in_worker_thread(self):
        from vidlens import server

        async def scenario():
            started = time.monotonic()
            task = asyncio.to_thread(time.sleep, 0.12)
            await asyncio.sleep(0)
            event_loop_lag = time.monotonic() - started
            await task
            return event_loop_lag

        self.assertLess(asyncio.run(scenario()), 0.1)
        self.assertTrue(callable(server._look))


class VideoFallbackTests(unittest.TestCase):
    def test_opencv_contact_sheet_pipeline_is_available(self):
        try:
            import cv2
            import numpy as np
        except ImportError:
            self.skipTest("OpenCV is not installed")

        from vidlens.media import stitch_sheet
        frames = [np.full((20, 30, 3), 180, dtype=np.uint8) for _ in range(3)]
        encoded = stitch_sheet(frames, columns=3, cell_scale=1.0)
        decoded = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded.shape[0], 46)


if __name__ == "__main__":
    unittest.main()
