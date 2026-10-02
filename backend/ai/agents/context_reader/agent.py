from __future__ import annotations

from ai.common import AgentResult
import json
import re

class ContextReaderAgent:
    name = "context_reader"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, source, retrieved_context=None):

        system = """
You are the Context Reader Agent in a governed technical documentation
pipeline.

Extract ONLY information explicitly supported by the supplied source.

Return valid JSON with exactly these keys:

summary
facts
changes
requirements
entities
gaps
contradictions
source_refs

Rules:

- Never invent missing information.
- Preserve technical names exactly.
- Preserve API paths exactly.
- Preserve versions, dates and metrics exactly.
- Facts should contain source references whenever available.
- Distinguish "not documented" from "not supported".
- Missing evidence must be recorded under gaps.
- Contradictory source information must be recorded under contradictions.
"""

        fallback = self._fallback(source)

        user = f"""
TITLE: {job.title}
CONTENT TYPE: {job.content_type}
AUDIENCE: {job.audience}

SOURCE DOCUMENT:
{source}

RETRIEVED KNOWLEDGE BASE EXCERPTS (same content job only):
{json.dumps(retrieved_context or [], ensure_ascii=False)}
"""

        output = await self.ai.generate_json(
            system,
            user,
            fallback=fallback,
        )

        return AgentResult(self.name, output)

    def _fallback(self, source):

        refs = re.findall(
            r"\[SOURCE: ([^\]]+)\]",
            source,
        )

        facts = []

        for block in source.split("\n\n"):

            lines = block.splitlines()

            if len(lines) >= 2 and lines[0].startswith("[SOURCE:"):

                facts.append(
                    {
                        "fact": " ".join(lines[1:])[:800],
                        "source_refs": [lines[0][9:-1]],
                    }
                )

            if len(facts) >= 20:
                break

        return {
            "summary": "Deterministically extracted source-grounded context.",
            "facts": facts,
            "changes": [],
            "requirements": [],
            "entities": [],
            "gaps": [
                "AI provider unavailable; deterministic extraction was used."
            ],
            "contradictions": [],
            "source_refs": refs,
        }


# ============================================================
