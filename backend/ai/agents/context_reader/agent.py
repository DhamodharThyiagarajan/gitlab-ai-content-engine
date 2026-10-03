from __future__ import annotations

from ai.prompts import get_prompt
from ai.common import AgentResult, gap_hint, split_sentences
import json
import re

class ContextReaderAgent:
    name = "context_reader"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, source, retrieved_context=None):

        system = get_prompt("context_reader")

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
        """Deterministic, source-grounded extraction used when no LLM is available."""
        refs, facts, gaps = [], [], []
        for block in re.split(r"\n\s*\n", source):
            lines = block.strip().splitlines()
            if not lines:
                continue
            ref = ""
            if lines[0].startswith("[SOURCE:"):
                ref = lines[0][len("[SOURCE:"):].rstrip("]").strip()
                refs.append(ref)
                lines = lines[1:]
            for sentence in split_sentences(" ".join(lines)):
                if gap_hint(sentence):
                    gaps.append(sentence[:300])
                elif len(facts) < 30:
                    facts.append({"fact": sentence[:500], "source_refs": [ref] if ref else []})
        return {
            "summary": "Deterministically extracted source-grounded context (no LLM used).",
            "facts": facts,
            "changes": [],
            "requirements": [],
            "entities": [],
            "gaps": gaps,
            "contradictions": [],
            "source_refs": list(dict.fromkeys(refs)),
        }
