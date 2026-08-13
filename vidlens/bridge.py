# -*- coding: utf-8 -*-
"""Vision bridge: send JPEG bytes + a text prompt to a vision model.

Works with any endpoint that follows the OpenAI chat/completions format.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.request
import urllib.error


class Bridge:
    """Thin client for an OpenAI-compatible vision API."""

    def __init__(self, endpoint, secret, model,
                 max_tokens=4000, temperature=0.1, timeout=120):
        self.endpoint = endpoint.rstrip("/")
        self.secret = secret
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout

    @classmethod
    def from_config(cls, cfg):
        """Build a Bridge from a config dict."""
        # New keys are primary; old keys kept as backward-compatible fallback.
        endpoint = cfg.get("api_url") or cfg.get("endpoint") or ""
        secret = cfg.get("api_key") or cfg.get("secret") or ""
        model = cfg.get("model_name") or cfg.get("vision_model") or cfg.get("model") or ""
        if not endpoint or not model:
            raise ValueError(
                "Config incomplete. Set 'api_url', 'api_key', and "
                "'model_name' in config.yaml."
            )
        return cls(endpoint, secret, model,
                   max_tokens=cfg.get("response_tokens", 4000),
                   temperature=cfg.get("sampling_temp", 0.1),
                   timeout=cfg.get("http_timeout", 120))

    def ask(self, image_bytes, prompt):
        """Send one image + prompt, return the model's text response."""
        b64 = base64.b64encode(image_bytes).decode("ascii")
        data_url = "data:image/jpeg;base64," + b64
        url = self.endpoint + "/chat/completions"
        payload = {
            "model": self.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        headers = {"Content-Type": "application/json"}
        if self.secret:
            headers["Authorization"] = "Bearer " + self.secret
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            result = json.loads(resp.read().decode("utf-8"))
            choices = result.get("choices")
            if not choices or "message" not in choices[0]:
                err = result.get("error", {})
                msg = err.get("message", str(result))[:500] if isinstance(err, dict) else str(result)[:500]
                raise RuntimeError("Unexpected API response: {}".format(msg))
            return choices[0]["message"]["content"].strip()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:500]
            raise RuntimeError("HTTP {}: {}".format(exc.code, detail))
        except urllib.error.URLError as exc:
            raise RuntimeError("Connection error: {}".format(exc.reason))


def load_config(config_path=None):
    """Load config.yaml, then apply VIDLENS_* env-var overrides."""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "config.yaml")
    cfg = {}
    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except ImportError:
        try:
            cfg = _parse_flat_yaml(config_path)
        except (FileNotFoundError, OSError):
            cfg = {}
    except FileNotFoundError:
        cfg = {}
    return apply_env_overrides(cfg)


def apply_env_overrides(cfg):
    """Apply VIDLENS_* environment variable overrides to a config dict."""
    if os.environ.get("VIDLENS_API_URL"):
        cfg["api_url"] = os.environ["VIDLENS_API_URL"]
    elif os.environ.get("VIDLENS_ENDPOINT"):
        cfg["api_url"] = os.environ["VIDLENS_ENDPOINT"]
    if os.environ.get("VIDLENS_API_KEY"):
        cfg["api_key"] = os.environ["VIDLENS_API_KEY"]
    elif os.environ.get("VIDLENS_SECRET"):
        cfg["api_key"] = os.environ["VIDLENS_SECRET"]
    if os.environ.get("VIDLENS_MODEL"):
        cfg["model_name"] = os.environ["VIDLENS_MODEL"]
    return cfg


def _parse_flat_yaml(path):
    """Minimal YAML reader for flat key:value files (no pyyaml needed)."""
    result = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            key, _, raw = stripped.partition(":")
            key = key.strip()
            raw = raw.strip()
            if raw.startswith('"'):
                end = raw.find('"', 1)
                raw = raw[1:end] if end > 0 else raw[1:]
            elif raw.startswith("'"):
                end = raw.find("'", 1)
                raw = raw[1:end] if end > 0 else raw[1:]
            else:
                hash_pos = raw.find(" #")
                if hash_pos > 0:
                    raw = raw[:hash_pos].strip()
            if raw == "":
                result[key] = ""
                continue
            low = raw.lower()
            if low in ("true", "yes", "on"):
                result[key] = True
                continue
            if low in ("false", "no", "off"):
                result[key] = False
                continue
            try:
                raw = int(raw)
            except ValueError:
                try:
                    raw = float(raw)
                except ValueError:
                    pass
            result[key] = raw
    return result
