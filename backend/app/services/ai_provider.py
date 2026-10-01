from __future__ import annotations

import asyncio
import json
import re

import httpx

from app.config import settings


class AIProvider:

    async def generate(self, system: str, user: str) -> str:
        # Mock mode
        if settings.ai_provider == "mock" or not settings.openai_api_key:
            return self.mock(system, user)

        model = settings.openai_model or "gemini-3.8-flash"

        url = (
            "https://generativelanguage.googleapis.com"
            f"/v1beta/models/{model}:generateContent"
        )

        headers = {
            "x-goog-api-key": settings.openai_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "systemInstruction": {
                "parts": [
                    {
                        "text": system
                    }
                ]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.15
            }
        }

        retry_delays = [0, 2, 5]

        async with httpx.AsyncClient(
            timeout=settings.ai_timeout_seconds
        ) as client:

            last_error = None

            for delay in retry_delays:

                if delay:
                    await asyncio.sleep(delay)

                try:
                    response = await client.post(
                        url,
                        headers=headers,
                        json=payload,
                    )

                    # Retry temporary Google server errors.
                    if response.status_code in {
                        500,
                        502,
                        503,
                        504,
                    }:
                        last_error = response
                        continue

                    # Don't retry permanent errors such as 400/401/403/404.
                    response.raise_for_status()

                    data = response.json()

                    candidates = data.get("candidates", [])

                    if not candidates:
                        raise RuntimeError(
                            f"Gemini returned no candidates: {data}"
                        )

                    content = candidates[0].get(
                        "content",
                        {}
                    )

                    parts = content.get(
                        "parts",
                        []
                    )

                    texts = [
                        part.get("text", "")
                        for part in parts
                        if isinstance(part, dict)
                        and part.get("text")
                    ]

                    if not texts:
                        raise RuntimeError(
                            f"Gemini returned no text: {data}"
                        )

                    return "\n".join(texts).strip()

                except httpx.HTTPError as exc:
                    last_error = exc

                    response_obj = getattr(
                        exc,
                        "response",
                        None
                    )

                    if response_obj is not None:
                        if response_obj.status_code not in {
                            500,
                            502,
                            503,
                            504,
                        }:
                            raise

                    continue

            if isinstance(last_error, httpx.Response):
                last_error.raise_for_status()

            if last_error:
                raise last_error

            raise RuntimeError(
                "Gemini request failed after retries."
            )

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

        return (
            f"# {title}\n\n"
            "## Summary\n"
            "Local mock mode is active. Configure "
            "AI_PROVIDER and OPENAI_API_KEY for "
            "model-based agents.\n\n"
            "## Source-grounded material\n"
            f"{source[:3000]}\n\n"
            "## Review note\n"
            "Human technical review is required "
            "before publication."
        )