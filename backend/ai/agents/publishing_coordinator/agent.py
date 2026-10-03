from __future__ import annotations

from ai.prompts import get_prompt
from ai.common import AgentResult, clean_markdown
import json

class PublishingCoordinatorAgent:
    name = "publishing_coordinator"

    def __init__(self, ai):
        self.ai = ai

    async def run(
        self,
        job,
        draft,
        review,
        context,
    ):

        system = get_prompt("publishing_coordinator")

        user = f"""
TITLE:
{job.title}

CHANNEL:
{job.channel}

DOCUMENT:
{draft}

TECHNICAL REVIEW:
{json.dumps(review, indent=2)}

SOURCE REFERENCES:
{json.dumps(context.get("source_refs", []))}
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
