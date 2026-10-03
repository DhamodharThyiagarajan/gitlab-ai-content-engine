"""Versioned prompt registry.

Prompts live as Markdown files in ai/prompts/<version>/<agent>.md so that any
change is a reviewable diff. PROMPT_VERSION is stored in the audit log of every
workflow run, so quality changes can be traced back to a prompt revision.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

PROMPT_VERSION = "v1"
_PROMPT_DIR = Path(__file__).parent
def _find_data_dir() -> Path:
    import os
    env = os.getenv("KNOWLEDGE_DATA_DIR")
    candidates = [Path(env)] if env else []
    here = Path(__file__).resolve()
    candidates += [here.parents[3] / "data", here.parents[2] / "knowledge_data", here.parents[2] / "data"]
    for c in candidates:
        if (c / "style_guides").exists():
            return c
    return candidates[0] if candidates else here.parents[3] / "data"


_DATA_DIR = _find_data_dir()

# Maps the content_type values used by the frontend to guide/template names.
_TYPE_ALIASES = {
    "release_notes": "release_notes",
    "documentation": "documentation",
    "api_docs": "api_reference",
    "api_reference": "api_reference",
    "blog_post": "developer_blog",
    "blog": "developer_blog",
    "onboarding_guide": "onboarding_guide",
    "custom": "documentation",
}


@lru_cache(maxsize=None)
def get_prompt(name: str, version: str = PROMPT_VERSION) -> str:
    path = _PROMPT_DIR / version / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {version}/{name}")
    return path.read_text(encoding="utf-8").strip()


def _read(folder: str, name: str) -> str:
    path = _DATA_DIR / folder / f"{name}.md"
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def style_guidance(content_type: str) -> str:
    """Return the GitLab voice guide plus the template for this content type."""
    key = _TYPE_ALIASES.get((content_type or "").lower(), "documentation")
    voice = _read("style_guides", "gitlab_voice")
    channel = _read("style_guides", key)
    template = _read("content_templates", key)
    parts = []
    if voice:
        parts.append("GITLAB VOICE GUIDE:\n" + voice)
    if channel:
        parts.append(f"CHANNEL RULES ({key}):\n" + channel)
    if template:
        parts.append(f"REQUIRED STRUCTURE ({key}):\n" + template)
    return "\n\n".join(parts)
