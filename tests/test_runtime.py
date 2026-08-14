import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = ROOT / "scripts" / "vidlens.py"


def load_runtime():
    spec = importlib.util.spec_from_file_location("vidlens_runtime_test", RUNTIME_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime()

    def test_native_pixels_guard_is_explicit(self):
        rule = self.runtime.AGENTS_RULE
        self.assertIn("path or URL is TEXT", rule)
        self.assertIn("explicitly known to support vision", rule)
        self.assertIn("may be loaded into native input", rule)
        self.assertIn("use native vision", rule)
        self.assertIn("explicitly known to support", rule)
        self.assertIn("capability is unknown", rule)
        self.assertIn("do not retry it", rule)

    def test_mcp_tool_descriptions_guard_native_vision(self):
        from vidlens.server import _tool_definitions

        descriptions = {tool.name: tool.description for tool in _tool_definitions()}
        self.assertIn("do not call this tool", descriptions["look"])
        self.assertIn("returns text only", descriptions["look"])
        self.assertIn("Skip it when native image pixels", descriptions["find_and_look"])

    def test_named_prompt_combines_acceptance_context(self):
        prompt = self.runtime.resolve_prompt(
            prompt="The chart should show 3 labeled bars.",
            prompt_name="verify_output",
            kind="image",
        )
        self.assertIn("VERDICT: PASS, FAIL, or UNCLEAR", prompt)
        self.assertIn("Agent context / intended result:", prompt)
        self.assertIn("The chart should show 3 labeled bars.", prompt)

    def test_verification_prompt_gets_smaller_token_budget(self):
        cfg = {"response_tokens": 1200, "verification_tokens": 350}
        verification = "VERDICT: PASS\nNEXT FIX: none"
        description = "Describe this chart in detail."
        self.assertEqual(self.runtime.response_token_budget(verification, cfg), 350)
        self.assertEqual(self.runtime.response_token_budget(description, cfg), 1200)

    def test_total_timeout_stops_provider_failover(self):
        cfg = {"http_timeout": 45, "total_timeout": 0}
        providers = [
            ("https://primary.test/v1", "key", "model"),
            ("https://fallback.test/v1", "key", "model"),
        ]
        with mock.patch.object(self.runtime, "build_provider_chain", return_value=providers):
            with mock.patch.object(
                self.runtime,
                "_call_one_provider",
                side_effect=AssertionError("provider should not run"),
            ) as call:
                with self.assertRaisesRegex(RuntimeError, "total_timeout expired"):
                    self.runtime.analyze_image(cfg, Path("image.png"), "image", "prompt")
        call.assert_not_called()

    def test_prepare_image_downscales_large_images(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow is not installed")

        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "large.png"
            Image.new("RGB", (3200, 1800), "white").save(source)
            prepared = self.runtime.prepare_image(
                source,
                {"max_image_side": 1600, "image_jpeg_quality": 90},
                Path(temporary),
            )
            with Image.open(prepared) as image:
                self.assertLessEqual(max(image.size), 1600)


if __name__ == "__main__":
    unittest.main()
