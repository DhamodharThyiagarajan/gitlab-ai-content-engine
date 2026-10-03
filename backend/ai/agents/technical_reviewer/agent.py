from __future__ import annotations

from ai.prompts import get_prompt
from ai.common import AgentResult
import json

class TechnicalReviewerAgent:
    name = "technical_reviewer"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, draft, context):

        system = get_prompt("technical_reviewer")

        fallback = {
            "verdict": "NEEDS_REVIEW",
            "risks": [
                "LLM technical review unavailable; only the automated grounding check was applied."
            ],
            "unsupported_claims": [],
            "missing_information": context.get("gaps", []),
            "supported_sections": [],
        }

        user = f"""
CONTENT TYPE:
{job.content_type}

EVIDENCE MAP:
{json.dumps(context, indent=2)}

DOCUMENT:
{draft}
"""

        output = await self.ai.generate_json(
            system,
            user,
            fallback=fallback,
        )

        return AgentResult(self.name, output)


# ============================================================
