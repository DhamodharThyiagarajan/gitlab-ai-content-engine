from __future__ import annotations

from ai.common import AgentResult, clean_markdown

class DocumentationWriterAgent:
    name = "documentation_writer"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, context, source):

        system = """
You are the Documentation Writer Agent.

Write professional customer-facing technical documentation.

Use ONLY facts supported by the supplied evidence and source.

STRICT RULES:

- Never invent features.
- Never invent API endpoints.
- Never invent metrics.
- Never invent dates.
- Never invent compatibility information.
- Never invent migration instructions.

If something is unknown, say:

"The available source material does not specify this."

Do NOT include:

- reviewer warnings
- reviewer verdicts
- evidence JSON
- internal QA notes
- workflow commentary
- human approval status

Use clean Markdown.

DO NOT escape Markdown characters.

Correct:
**Security**

Incorrect:
\\*\\*Security:\\*\\*

Correct:
`GET /api/v2/example`

Incorrect:
\\`GET /api/v2/example\\`

Use descriptive headings.

Do not add emojis.
"""

        user = f"""
TITLE: {job.title}
TYPE: {job.content_type}
AUDIENCE: {job.audience}
CHANNEL: {job.channel}

EVIDENCE:
{json.dumps(context, indent=2)}

SOURCE:
{source}
"""

        result = await self.ai.generate(system, user)

        return AgentResult(
            self.name,
            clean_markdown(result),
        )


# ============================================================
