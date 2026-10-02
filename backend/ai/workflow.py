from __future__ import annotations

import json

from app.services.ai_provider import AIProvider
from ai.common import clean_markdown, document_metadata, clean_review_items, clean_source_refs, fact_text, fact_sources
from ai.agents.crew import build_crew
from ai.retrieval.knowledge_base import KnowledgeBase


class ContentWorkflow:

    def __init__(self):
        self.ai = AIProvider()
        self.knowledge_base = None
        self.crew = None

    def _retrieve_context(self, job, source):
        """Use Chroma retrieval when installed; direct source processing remains available."""
        try:
            if self.knowledge_base is None:
                self.knowledge_base = KnowledgeBase()
            self.knowledge_base.add_source(job.id, source)
            query = " ".join(
                str(value) for value in
                (job.title, job.content_type, job.audience, job.product_area)
                if value
            )
            return self.knowledge_base.retrieve(job.id, query)
        except (ImportError, ModuleNotFoundError):
            return []

    def _extract_crew_text(self, crew_result):
        if crew_result is None:
            return ""

        if hasattr(crew_result, "tasks_output"):
            tasks = crew_result.tasks_output
            if tasks:
                # The last task is the publishing coordinator. Earlier outputs
                # contain evidence and review data, not customer-facing content.
                task = tasks[-1]
                if hasattr(task, "output"):
                    output = task.output
                elif isinstance(task, dict):
                    output = task.get("output") or task.get("content") or task
                else:
                    output = task
                return str(output) if tasks else ""

        if isinstance(crew_result, list):
            return "\n\n".join(str(item) for item in crew_result)

        if isinstance(crew_result, dict):
            for key in ("output", "content", "final_output", "result"):
                if key in crew_result:
                    return str(crew_result[key])
            return str(crew_result)

        return str(crew_result)

    def _task_texts(self, crew_result):
        tasks = getattr(crew_result, "tasks_output", None) or []
        return [str(getattr(task, "output", task)) for task in tasks]

    def _parse_task_json(self, value):
        if not value:
            return None
        value = value.strip()
        if value.startswith("```"):
            value = value.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        try:
            result = json.loads(value)
            return result if isinstance(result, dict) else None
        except json.JSONDecodeError:
            return None

    async def run(self, job):
        source = (job.source_text or "").strip()
        retrieved_context = self._retrieve_context(job, source)

        task_inputs = {
            "context_reader": (
                f"Extract source-grounded facts, gaps, and source references for '{job.title}'. "
                "Return JSON with keys summary, facts, gaps, contradictions, source_refs. Each fact must "
                "include its source reference when available. Do not reproduce the source document.\n\n"
                f"SOURCE DOCUMENT:\n{source[:8000]}"
            ),
            "documentation_writer": (
                f"Using the preceding evidence extraction, write original, concise, professional Markdown "
                f"documentation for '{job.title}' for '{job.audience}'. Use only supported facts. "
                "Do not copy the source verbatim, include the evidence JSON, or repeat the source."
            ),
            "technical_reviewer": (
                "Compare the preceding draft against the evidence extraction. Return JSON with keys verdict "
                "(PASS or NEEDS_REVIEW), risks, unsupported_claims, missing_information, supported_sections. "
                "Do not rewrite or reproduce the source."
            ),
            "tone_optimizer": (
                "Revise the preceding documentation using the review findings. Improve clarity and structure "
                "without adding facts. Return the revised customer-facing Markdown only."
            ),
            "publishing_coordinator": (
                f"Prepare the final customer-facing Markdown document for '{job.title}' from the preceding "
                "revised draft. Preserve supported limitations, omit internal review/evidence data, and do "
                "not copy or repeat the source document. Return Markdown only."
            ),
        }

        self.crew = build_crew(self.ai, task_inputs)
        crew_result = self.crew.kickoff()
        crew_text = self._extract_crew_text(crew_result)
        task_texts = self._task_texts(crew_result)
        evidence = self._parse_task_json(task_texts[0] if task_texts else None) or {}
        technical = self._parse_task_json(task_texts[2] if len(task_texts) > 2 else None) or {}

        final_document = clean_markdown(crew_text)
        if not final_document:
            final_document = "The source material did not produce a usable draft."

        lines = final_document.splitlines()
        if lines and lines[0].strip().startswith("# "):
            lines = lines[1:]
        final_document = "\n".join(lines).strip()

        metadata = document_metadata()
        body = final_document.strip()
        if body.startswith("# "):
            body = "\n".join(body.splitlines()[1:]).strip()

        final_content = clean_markdown(
            f"# 🚀 {job.title}\n\n"
            f"## 📌 Quick overview\n\n"
            f"- **Date:** {metadata['date']} ({metadata['timezone']})\n"
            f"- **Time:** {metadata['time']}\n"
            f"- **Content type:** {job.content_type}\n"
            f"- **Audience:** {job.audience}\n"
            f"- **Channel:** {job.channel}\n\n"
            f"## 🎯 Summary\n\n"
            f"{body or 'The available source material does not specify detailed content for this section.'}\n\n"
            f"## ✅ Key takeaways\n\n"
            f"- Source-backed content was prepared for the requested {job.content_type.lower()} output.\n"
            f"- The draft is tailored for the {job.audience} audience.\n"
            f"- Final review is still recommended before publishing.\n"
        )

        risks = clean_review_items(technical.get("risks", []))
        unsupported_claims = clean_review_items(technical.get("unsupported_claims", []))
        gaps = clean_review_items(evidence.get("gaps", []))
        source_refs = clean_source_refs(evidence.get("source_refs", []))
        if not isinstance(retrieved_context, list):
            retrieved_context = []
        score = max(0, 100 - min(40, 15 * len(unsupported_claims)) - min(30, 10 * len(risks)) - min(20, 3 * len(gaps)))
        if not technical:
            risks.append("Structured technical review was unavailable; human review is required.")
            score = min(score, 70)
        context_payload = {
            **evidence,
            "source_refs": source_refs,
            "retrieved_context": retrieved_context,
            "summary": evidence.get("summary", "CrewAI handled source-grounded generation; the workflow now packages the final Markdown."),
        }

        return {
            "context": json.dumps(context_payload, indent=2),
            "content": final_content,
            "risks": risks + unsupported_claims,
            "quality_score": score,
            "technical_review": json.dumps(
                {
                    "verdict": technical.get("verdict", "NEEDS_REVIEW"),
                    "risks": risks,
                    "unsupported_claims": unsupported_claims,
                    "missing_information": technical.get("missing_information", gaps),
                    "supported_sections": technical.get("supported_sections", []),
                    "supported_information": [
                        {"fact": fact_text(item), "source_refs": clean_source_refs(fact_sources(item))}
                        for item in evidence.get("facts", [])
                        if fact_text(item)
                    ] if isinstance(evidence.get("facts", []), list) else [],
                    "context_gaps": gaps,
                    "source_refs": source_refs,
                    "quality_score": score,
                    "generated_at": metadata["iso"],
                    "human_approval_required": True,
                },
                indent=2,
            ),
            "generated_at": metadata["iso"],
            "crewai_output": crew_text,
            "agent_trace": [
                {"agent": agent, "status": "completed"}
                for agent in (
                    "context_reader",
                    "documentation_writer",
                    "technical_reviewer",
                    "tone_optimizer",
                    "publishing_coordinator",
                )
            ],
        }

