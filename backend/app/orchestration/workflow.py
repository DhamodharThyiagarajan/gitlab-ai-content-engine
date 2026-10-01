from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from app.services.ai_provider import AIProvider


@dataclass
class AgentResult:
    name: str
    output: dict | str


# ============================================================
# HELPERS
# ============================================================

def clean_markdown(text: str) -> str:
    """Normalize Markdown returned by the AI."""

    if not text:
        return ""

    text = str(text).strip()

    replacements = {
        r"\*\*": "**",
        r"\*": "*",
        r"\`": "`",
        r"\_": "_",
        r"\|": "|",
        r"\#": "#",
        r"\>": ">",
        r"\---": "---",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize AI-generated numbered lists such as:
    # 1) item / 2) item
    # into bullet lists to avoid broken numbering.
    text = re.sub(
        r"(?m)^\s*\d+[\.\)]\s+",
        "- ",
        text,
    )

    return text.strip()


def document_metadata() -> dict:
    """Generate real backend timestamp in IST."""

    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    return {
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M:%S %p"),
        "timezone": "IST",
        "iso": now.isoformat(),
    }


def fact_text(item) -> str:
    """Extract readable claim from different AI JSON structures."""

    if isinstance(item, dict):
        return str(
            item.get("fact")
            or item.get("claim")
            or item.get("text")
            or item.get("description")
            or ""
        ).strip()

    return str(item).strip()


def fact_sources(item) -> list[str]:
    """Extract source references from different AI JSON structures."""

    if not isinstance(item, dict):
        return []

    refs = (
        item.get("source_refs")
        or item.get("sources")
        or item.get("source")
        or []
    )

    if isinstance(refs, str):
        return [refs]

    if isinstance(refs, list):
        return [str(x).strip() for x in refs if str(x).strip()]

    return []


def format_facts(facts) -> str:
    """Pretty-print evidence instead of Python dictionaries."""

    if not facts:
        return "- No structured evidence was extracted."

    output = []

    for item in facts:
        claim = fact_text(item)

        if not claim:
            continue

        output.append(f"- {claim}")

        for source in fact_sources(item):
            output.append(f"  - 📚 Source: {source}")

    return "\n".join(output) or "- No structured evidence was extracted."


def format_items(items, empty_message: str) -> str:
    """Create deterministic Markdown bullet lists."""

    cleaned = []

    for item in items or []:
        if isinstance(item, dict):
            value = (
                item.get("fact")
                or item.get("claim")
                or item.get("description")
                or item.get("text")
                or json.dumps(item, ensure_ascii=False)
            )
        else:
            value = str(item)

        value = str(value).strip()

        if value:
            cleaned.append(value)

    if not cleaned:
        return f"- {empty_message}"

    return "\n".join(f"- {x}" for x in cleaned)


# ============================================================
# CONTEXT READER
# ============================================================

class ContextReaderAgent:
    name = "context_reader"

    def __init__(self, ai):
        self.ai = ai

    async def run(self, job, source):

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
# DOCUMENTATION WRITER
# ============================================================

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
# TECHNICAL REVIEWER
# ============================================================

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
# TONE OPTIMIZER
# ============================================================

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
# PUBLISHING COORDINATOR
# ============================================================

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
# WORKFLOW
# ============================================================

class ContentWorkflow:

    def __init__(self):

        self.ai = AIProvider()

        self.context_agent = ContextReaderAgent(self.ai)

        self.writer = DocumentationWriterAgent(self.ai)

        self.reviewer = TechnicalReviewerAgent(self.ai)

        self.tone = ToneOptimizerAgent(self.ai)

        self.publisher = PublishingCoordinatorAgent(self.ai)

    async def run(self, job):

        source = (job.source_text or "").strip()

        # ----------------------------------------------------
        # AGENT 1 — CONTEXT
        # ----------------------------------------------------

        context = (
            await self.context_agent.run(
                job,
                source,
            )
        ).output

        # ----------------------------------------------------
        # AGENT 2 — DOCUMENTATION
        # ----------------------------------------------------

        draft = (
            await self.writer.run(
                job,
                context,
                source,
            )
        ).output

        # ----------------------------------------------------
        # AGENT 3 — TECHNICAL REVIEW
        # ----------------------------------------------------

        technical = (
            await self.reviewer.run(
                job,
                draft,
                context,
            )
        ).output

        # ----------------------------------------------------
        # AGENT 4 — TONE
        # ----------------------------------------------------

        tone = (
            await self.tone.run(
                job,
                draft,
                technical,
            )
        ).output

        # ----------------------------------------------------
        # AGENT 5 — PUBLISHING PREPARATION
        # ----------------------------------------------------

        final_document = (
            await self.publisher.run(
                job,
                tone,
                technical,
                context,
            )
        ).output

        final_document = clean_markdown(
            final_document
        )

        # ----------------------------------------------------
        # METADATA
        # ----------------------------------------------------

        metadata = document_metadata()

        facts = context.get(
            "facts",
            [],
        )

        source_refs = context.get(
            "source_refs",
            [],
        )

        context_gaps = [
            str(x).strip()
            for x in context.get("gaps", [])
            if str(x).strip()
        ]

        unsupported = [
            str(x).strip()
            for x in technical.get(
                "unsupported_claims",
                [],
            )
            if str(x).strip()
        ]

        technical_risks = [
            str(x).strip()
            for x in technical.get(
                "risks",
                [],
            )
            if str(x).strip()
        ]

        missing = [
            str(x).strip()
            for x in technical.get(
                "missing_information",
                [],
            )
            if str(x).strip()
        ]

        verdict = technical.get(
            "verdict",
            "NEEDS_REVIEW",
        )

        # ----------------------------------------------------
        # REMOVE DUPLICATE AI TITLE
        # ----------------------------------------------------

        lines = final_document.splitlines()

        if lines and lines[0].strip().startswith("# "):
            lines = lines[1:]

        final_document = "\n".join(lines).strip()

        # ----------------------------------------------------
        # QUALITY SCORE
        # ----------------------------------------------------

        score = 100

        # Unsupported claims are serious.
        score -= min(
            40,
            len(unsupported) * 15,
        )

        # Other technical risks.
        score -= min(
            25,
            len(technical_risks) * 10,
        )

        # Context gaps reduce completeness but do not
        # necessarily mean the document is wrong.
        score -= min(
            20,
            len(context_gaps) * 3,
        )

        # Reviewer-discovered missing information.
        score -= min(
            10,
            len(missing) * 2,
        )

        if verdict != "PASS":
            score -= 10

        score = max(
            0,
            min(100, score),
        )

        # The stored draft is the customer-facing Markdown only. Review evidence
        # is returned separately and stored in reviewer_notes.
        final_content = clean_markdown(
            f"# {job.title}\n\n"
            f"**Documentation generated:** {metadata['date']}  \n"
            f"**Generated at:** {metadata['time']} {metadata['timezone']}  \n"
            f"**Content type:** {job.content_type}  \n"
            f"**Audience:** {job.audience}  \n"
            f"**Channel:** {job.channel}\n\n---\n\n"
            f"{final_document}"
        )
        # RISKS STORED IN DATABASE

        risks = []

        risks.extend(
            unsupported
        )

        risks.extend(
            technical_risks
        )

        risks.extend(
            f"Context gap: {gap}"
            for gap in context_gaps
        )

        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        return {
            "context": json.dumps(
                context,
                indent=2,
            ),

            "content": final_content,

            "risks": risks,

            "quality_score": score,

            "technical_review": json.dumps(
                {
                    **technical,
                    "supported_information": [
                        {
                            "fact": fact_text(item),
                            "source_refs": fact_sources(item),
                        }
                        for item in facts
                        if fact_text(item)
                    ],
                    "context_gaps": context_gaps,
                    "source_refs": source_refs,
                    "quality_score": score,
                    "generated_at": metadata["iso"],
                    "evidence_count": len(facts),
                    "human_approval_required": True,
                },
                indent=2,
            ),

            "generated_at": metadata["iso"],

            "agent_trace": [
                {
                    "agent": agent,
                    "status": "completed",
                }
                for agent in [
                    "context_reader",
                    "documentation_writer",
                    "technical_reviewer",
                    "tone_optimizer",
                    "publishing_coordinator",
                ]
            ],
        }
