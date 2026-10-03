from __future__ import annotations

import json
import re

import httpx

from app.config import settings


class AIProvider:
    async def generate(self, system: str, user: str) -> str:
        if settings.ai_provider.lower() == "mock":
            return self.mock(system, user)
        if settings.ai_provider.lower() != "openai_compatible":
            raise RuntimeError(f"Unsupported AI_PROVIDER: {settings.ai_provider}")
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required when AI_PROVIDER=openai_compatible")

        url = f"{settings.openai_base_url.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
        payload = {
            "model": settings.openai_model,
            "temperature": 0.15,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        async with httpx.AsyncClient(timeout=settings.ai_timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
        choices = response.json().get("choices", [])
        if not choices:
            raise RuntimeError("AI provider returned no completion choices")
        content = choices[0].get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("AI provider returned an empty completion")
        return content.strip()

    async def generate_json(
        self,
        system: str,
        user: str,
        fallback,
    ):
        if (
            settings.ai_provider == "mock"
            or not settings.openai_api_key
        ):
            return fallback

        raw = await self.generate(
            system + "\nReturn valid JSON only.",
            user,
        )

        raw = raw.strip()

        # Remove Markdown JSON fences.
        if raw.startswith("```"):
            raw = re.sub(
                r"^```(?:json)?",
                "",
                raw,
                flags=re.IGNORECASE,
            ).strip()

            raw = re.sub(
                r"```$",
                "",
                raw,
            ).strip()

        try:
            value = json.loads(raw)

            if isinstance(value, dict):
                return value

            return fallback

        except json.JSONDecodeError:
            return fallback

    def mock(self, system: str, user: str) -> str:
        """Deterministic offline output so the full workflow is demoable without an API key."""
        if "Tone and Structure Agent" in system or "Publishing Coordinator Agent" in system:
            m = re.search(r"DOCUMENT:\n(.*?)(?:\n(?:TECHNICAL REVIEW|SOURCE REFERENCES|STYLE AND STRUCTURE GUIDANCE):|$)", user, re.S)
            return m.group(1).strip() if m else user.strip()

        title_match = re.search(r"TITLE:\s*(.+)", user)
        title = title_match.group(1).strip() if title_match else "Technical Update"
        facts, gaps, summary = [], [], ""
        ev = re.search(r"EVIDENCE:\n(.*?)\n\s*SOURCE:\n", user, re.S)
        if ev:
            try:
                data = json.loads(ev.group(1))
                facts, gaps, summary = data.get("facts", []), data.get("gaps", []), data.get("summary", "")
            except json.JSONDecodeError:
                pass
        lines = [f"# {title}", "", "## Overview", "",
                 "This document summarizes the changes described in the supplied source material.", "",
                 "## Key points", ""]
        for item in facts[:20]:
            text = item.get("fact", "") if isinstance(item, dict) else str(item)
            refs = item.get("source_refs", []) if isinstance(item, dict) else []
            if text:
                lines.append(f"- {text}" + (f" (Source: {', '.join(refs)})" if refs else ""))
        if not facts:
            lines.append("- The available source material does not specify this.")
        lines += ["", "## Limitations and open questions", ""]
        lines += [f"- {g}" for g in gaps] or ["- No gaps were detected in the supplied source material."]
        return "\n".join(lines)
