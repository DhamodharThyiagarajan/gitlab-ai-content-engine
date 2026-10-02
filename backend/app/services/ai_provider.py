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

    def mock(
        self,
        system: str,
        user: str,
    ) -> str:

        title_match = re.search(
            r"TITLE:\s*(.+)",
            user,
        )

        title = (
            title_match.group(1).strip()
            if title_match
            else "Technical Update"
        )

        match = re.search(
            r"SOURCE(?: DOCUMENT)?:\n"
            r"(.+?)"
            r"(?:\n(?:CONTEXT|TECHNICAL REVIEW|EVIDENCE MAP|DRAFT|SOURCE REFS):|$)",
            user,
            re.S,
        )

        source = (
            match.group(1).strip()
            if match
            else user[-3000:]
        )

        cleaned = re.sub(r"\s+", " ", source)
        sentences = [
            sentence.strip()
            for sentence in re.split(r"(?<=[.!?])\s+", cleaned)
            if sentence.strip()
        ]
        highlights = sentences[:4]
        if not highlights:
            highlights = [
                "The source material contains the key product details required for a technical draft.",
                "The content below summarizes the most relevant facts for the target audience.",
            ]

        summary_lines = "\n".join(f"- {item}" for item in highlights)

        return (
            f"# {title}\n\n"
            "## Overview\n\n"
            "This draft was generated from the uploaded source material in local mock mode. "
            "It is structured for review and publication while staying grounded in the available document context.\n\n"
            "## Executive summary\n\n"
            f"{summary_lines}\n\n"
            "## Key recommendations\n\n"
            "- Confirm the facts against the original source before publishing.\n"
            "- Tailor the final language to the intended audience and channel.\n"
            "- Complete a final human review pass for tone and product accuracy.\n\n"
            "## Supporting context\n\n"
            f"{source[:2000]}\n\n"
            "## Review note\n\n"
            "Human technical review is required before publication."
        )
