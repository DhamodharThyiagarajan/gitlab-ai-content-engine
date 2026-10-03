from __future__ import annotations

from ai.prompts import get_prompt
from ai.common import AgentResult, clean_markdown
import json

class ToneOptimizerAgent:
    name = "tone_optimizer"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, draft, review, guidance=""):

        system = get_prompt("tone_optimizer")

        user = f"""
AUDIENCE:
{job.audience}

CONTENT TYPE:
{job.content_type}

DOCUMENT:
{draft}

TECHNICAL REVIEW:
{json.dumps(review, indent=2)}

STYLE AND STRUCTURE GUIDANCE:
{guidance}
"""

        result = await self.ai.generate(
            system,
            user,
        )

        return AgentResult(
            self.name,
            clean_markdown(result),
        )


# ============================================================
