from __future__ import annotations

import json

from ai.prompts import get_prompt
from ai.common import AgentResult, clean_markdown

class DocumentationWriterAgent:
    name = "documentation_writer"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, context, source, guidance=""):

        system = get_prompt("documentation_writer")

        user = f"""
TITLE: {job.title}
TYPE: {job.content_type}
AUDIENCE: {job.audience}
CHANNEL: {job.channel}

EVIDENCE:
{json.dumps(context, indent=2)}

SOURCE:
{source}

STYLE AND STRUCTURE GUIDANCE:
{guidance}
"""

        result = await self.ai.generate(system, user)

        return AgentResult(
            self.name,
            clean_markdown(result),
        )


# ============================================================
