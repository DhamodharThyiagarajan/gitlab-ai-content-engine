from __future__ import annotations

from ai.common import AgentResult
import json

class TechnicalReviewerAgent:
    name = "technical_reviewer"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, draft, context):

        system = """
You are the Technical Reviewer Agent.

Compare the generated documentation against the evidence map.

Return JSON containing exactly:

verdict
risks
unsupported_claims
missing_information
supported_sections

verdict must be:

PASS

or

NEEDS_REVIEW

Rules:

- Identify unsupported claims.
- Identify claims stronger than the evidence.
- Identify missing technical information.
- Do not invent risks.
- Internal benchmark results must not become universal guarantees.
- "Not documented" does NOT automatically mean "not supported".
"""

        fallback = {
            "verdict": "NEEDS_REVIEW",
            "risks": [
                "AI technical review unavailable; human review required."
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
