from __future__ import annotations

from ai.common import AgentResult, clean_markdown
import json

class ToneOptimizerAgent:
    name = "tone_optimizer"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, draft, review):

        system = """
You are the Tone and Structure Agent.

Improve:

- clarity
- readability
- headings
- organization
- audience fit

Do NOT:

- add facts
- invent information
- include reviewer warnings
- include reviewer verdicts
- include internal QA notes
- include evidence JSON
- include human approval information

Remove or rewrite unsupported claims identified by the technical reviewer.

Return clean Markdown only.

Do not escape Markdown.

Do not add emojis.
"""

        user = f"""
AUDIENCE:
{job.audience}

CONTENT TYPE:
{job.content_type}

DOCUMENT:
{draft}

TECHNICAL REVIEW:
{json.dumps(review, indent=2)}
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
