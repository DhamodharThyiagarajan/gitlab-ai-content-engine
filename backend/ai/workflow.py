from __future__ import annotations

import asyncio
import json
import time

from app.config import settings
from app.services.ai_provider import AIProvider
from ai.common import (
    clean_markdown, document_metadata, clean_review_items, clean_source_refs,
    fact_text, fact_sources, ungrounded_claims,
)
from ai.prompts import PROMPT_VERSION, style_guidance
from ai.schemas.context import ContextSchema
from ai.retrieval.knowledge_base import KnowledgeBase
from ai.agents.context_reader.agent import ContextReaderAgent
from ai.agents.documentation_writer.agent import DocumentationWriterAgent
from ai.agents.technical_reviewer.agent import TechnicalReviewerAgent
from ai.agents.tone_optimizer.agent import ToneOptimizerAgent
from ai.agents.publishing_coordinator.agent import PublishingCoordinatorAgent

MIN_SOURCE_CHARS = 20


class InsufficientContext(ValueError):
    """Raised when the source material is too thin to draft from safely."""


class ContentWorkflow:
    """Context -> Draft -> Technical review -> Tone -> Publish prep.

    CrewAI orchestrates the five agents when a real LLM is configured. The same
    five agents are also available as plain async classes, which is the path used in
    mock mode and the automatic fallback if the CrewAI run fails.
    """

    def __init__(self):
        self.ai = AIProvider()
        self.knowledge_base = None
        self.crew = None
        self.trace: list[dict] = []

    # ------------------------------------------------------------------ retrieval
    def _retrieve_context(self, job, source):
        """Retrieve job-scoped chunks plus approved knowledge (style, terminology, prior docs)."""
        try:
            if self.knowledge_base is None:
                self.knowledge_base = KnowledgeBase()
            self.knowledge_base.add_source(job.id, source)
            self.knowledge_base.ensure_static_knowledge()
            query = " ".join(str(v) for v in (job.title, job.content_type, job.audience, job.product_area) if v)
            return self.knowledge_base.retrieve(job.id, query) + self.knowledge_base.retrieve_static(query)
        except Exception:  # retrieval is an enhancement; never block the workflow
            return []

    # ------------------------------------------------------------------ tracing
    async def _stage(self, name, coro):
        started = time.perf_counter()
        try:
            result = await coro
            self.trace.append({"agent": name, "status": "completed", "seconds": round(time.perf_counter() - started, 2)})
            return result
        except Exception as exc:
            self.trace.append({"agent": name, "status": "failed", "error": str(exc)[:300],
                               "seconds": round(time.perf_counter() - started, 2)})
            raise

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


    # ------------------------------------------------------------------ stage 1
    async def prepare_context(self, job) -> dict:
        """Normalize inputs and build the structured context pack (also used by POST /api/context-pack)."""
        source = (job.source_text or "").strip()
        if len(source) < MIN_SOURCE_CHARS:
            raise InsufficientContext("The source material is too short to prepare a context pack.")
        retrieved = self._retrieve_context(job, source)
        raw = (await self._stage("context_reader", ContextReaderAgent(self.ai).run(job, source[:12000], retrieved))).output
        raw = raw if isinstance(raw, dict) else {}
        known = {k: raw[k] for k in ContextSchema.model_fields if k in raw}
        try:
            context = ContextSchema(**known).model_dump()
        except Exception:
            context = ContextSchema().model_dump()
        context["source_refs"] = clean_source_refs(context.get("source_refs", []))
        context["retrieved_context"] = retrieved if isinstance(retrieved, list) else []
        if not context["facts"]:
            raise InsufficientContext("No supported facts could be extracted from the source material.")
        return context

    # ------------------------------------------------------------------ CrewAI path
    async def _run_crew(self, job, source, guidance):
        from ai.agents.crew import build_crew
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
                "Do not copy the source verbatim, include the evidence JSON, or repeat the source.\n\n" + guidance
            ),
            "technical_reviewer": (
                "Compare the preceding draft against the evidence extraction. Return JSON with keys verdict "
                "(PASS or NEEDS_REVIEW), risks, unsupported_claims, missing_information, supported_sections. "
                "Do not rewrite or reproduce the source."
            ),
            "tone_optimizer": (
                "Revise the preceding documentation using the review findings. Improve clarity and structure "
                "without adding facts. Return the revised customer-facing Markdown only.\n\n" + guidance
            ),
            "publishing_coordinator": (
                f"Prepare the final customer-facing Markdown document for '{job.title}' from the preceding "
                "revised draft. Preserve supported limitations, omit internal review/evidence data, and do "
                "not copy or repeat the source document. Return Markdown only."
            ),
        }
        self.crew = build_crew(self.ai, task_inputs)
        started = time.perf_counter()
        crew_result = await asyncio.to_thread(self.crew.kickoff)  # CrewAI forbids sync kickoff inside an event loop
        elapsed = round(time.perf_counter() - started, 2)
        texts = self._task_texts(crew_result)
        evidence = self._parse_task_json(texts[0] if texts else None) or {}
        technical = self._parse_task_json(texts[2] if len(texts) > 2 else None) or {}
        final = clean_markdown(self._extract_crew_text(crew_result))
        if not final:
            raise RuntimeError("CrewAI returned an empty document")
        self.trace = [{"agent": a, "status": "completed", "orchestrator": "crewai",
                       "seconds": round(elapsed / 5, 2)} for a in
                      ("context_reader", "documentation_writer", "technical_reviewer", "tone_optimizer", "publishing_coordinator")]
        known = {k: evidence[k] for k in ContextSchema.model_fields if k in evidence}
        context = ContextSchema(**known).model_dump() if known else ContextSchema().model_dump()
        context["source_refs"] = clean_source_refs(context.get("source_refs", []))
        return context, technical, final

    # ------------------------------------------------------------------ direct path
    async def _run_direct(self, job, source, context, guidance):
        draft = (await self._stage("documentation_writer", DocumentationWriterAgent(self.ai).run(job, context, source[:12000], guidance))).output
        technical = (await self._stage("technical_reviewer", TechnicalReviewerAgent(self.ai).run(job, draft, context))).output
        toned = (await self._stage("tone_optimizer", ToneOptimizerAgent(self.ai).run(job, draft, technical, guidance))).output
        final = (await self._stage("publishing_coordinator", PublishingCoordinatorAgent(self.ai).run(job, toned, technical, context))).output
        return technical if isinstance(technical, dict) else {}, final

    # ------------------------------------------------------------------ main entry
    async def run(self, job):
        self.trace = []
        source = (job.source_text or "").strip()
        guidance = style_guidance(job.content_type)
        use_crew = settings.ai_provider.lower() != "mock" and settings.use_crewai
        orchestrator = "direct"
        fallback_note = None

        context = await self.prepare_context(job)  # raises InsufficientContext on thin input
        technical, final = {}, ""
        if use_crew:
            try:
                crew_context, technical, final = await self._run_crew(job, source, guidance)
                # Keep the richer context-reader output; use the crew's only if ours is empty.
                if not context.get("facts"):
                    context = {**context, **{k: v for k, v in crew_context.items() if v}}
                orchestrator = "crewai"
            except Exception as exc:
                fallback_note = f"CrewAI run failed ({str(exc)[:120]}); the direct agent pipeline was used instead."
                self.trace = [t for t in self.trace if t["agent"] == "context_reader"]
        if orchestrator == "direct":
            technical, final = await self._run_direct(job, source, context, guidance)

        body = clean_markdown(final) or "The available source material does not specify this."
        lines = body.splitlines()
        if lines and lines[0].strip().startswith("# "):
            body = "\n".join(lines[1:]).strip()

        metadata = document_metadata()
        refs = context.get("source_refs", [])
        sources_md = "\n".join(f"- {r}" for r in refs) or "- No source references were captured."
        content = clean_markdown(
            f"# {job.title}\n\n"
            f"> {job.content_type.replace('_', ' ').title()} for {job.audience} | Channel: {job.channel} | "
            f"Generated {metadata['date']} {metadata['time']} {metadata['timezone']}\n\n"
            f"{body}\n\n## Source references\n\n{sources_md}\n"
        )

        risks = clean_review_items(technical.get("risks", []))
        unsupported = clean_review_items(technical.get("unsupported_claims", []))
        for claim in ungrounded_claims(body, source):  # model-independent guard
            if claim not in unsupported:
                unsupported.append(claim)
        gaps = clean_review_items(context.get("gaps", []))
        contradictions = clean_review_items(context.get("contradictions", []))
        risks += [f"Contradiction in sources: {c}" for c in contradictions]
        if fallback_note:
            risks.append(fallback_note)

        score = max(0, 100 - min(40, 15 * len(unsupported)) - min(30, 10 * len(risks)) - min(20, 3 * len(gaps)))
        verdict = "PASS" if not unsupported and not contradictions and technical.get("verdict", "PASS") == "PASS" else "NEEDS_REVIEW"
        facts = context.get("facts", [])
        review = {
            "verdict": verdict,
            "risks": risks,
            "unsupported_claims": unsupported,
            "missing_information": gaps,
            "supported_sections": technical.get("supported_sections", []),
            "supported_information": [{"fact": fact_text(f), "source_refs": clean_source_refs(fact_sources(f))}
                                      for f in facts if fact_text(f)],
            "context_gaps": gaps,
            "source_refs": refs,
            "quality_score": score,
            "generated_at": metadata["iso"],
            "evidence_count": len(facts),
            "prompt_version": PROMPT_VERSION,
            "orchestrator": orchestrator,
            "human_approval_required": True,
        }
        return {
            "context": json.dumps(context, indent=2),
            "content": content,
            "risks": risks + unsupported,
            "quality_score": score,
            "technical_review": json.dumps(review, indent=2),
            "generated_at": metadata["iso"],
            "prompt_version": PROMPT_VERSION,
            "orchestrator": orchestrator,
            "agent_trace": self.trace,
        }
