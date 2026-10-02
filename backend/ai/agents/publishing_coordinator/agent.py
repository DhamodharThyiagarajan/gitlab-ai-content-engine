from __future__ import annotations

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

        system = """
You are the Publishing Coordinator Agent.

Prepare final customer-facing Markdown documentation.

Return ONLY the customer documentation.

Never include:

- technical review verdict
- reviewer warnings
- evidence JSON
- internal workflow information
- approval status
- unsupported claim lists
- internal QA comments

Preserve important customer-facing limitations.

Example:

GOOD:
"The source material does not specify the maximum export file size."

BAD:
"Reviewer Warning: export file size is missing."

Use clean Markdown.

Do not escape Markdown.

Do not add emojis.

Do not state that the document is approved.
"""

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
