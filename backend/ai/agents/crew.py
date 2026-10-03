from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor

from crewai import Agent, Crew, Process, Task
from crewai.llms.base_llm import BaseLLM

ROLE_DETAILS = {
    "context_reader": (
        "Context Reader",
        "Extract only source-grounded facts, gaps, and references as concise JSON.",
    ),
    "documentation_writer": (
        "Documentation Writer",
        "Create original, accurate, customer-facing technical documentation from evidence.",
    ),
    "technical_reviewer": (
        "Technical Reviewer",
        "Check the draft against evidence and return structured review findings as JSON.",
    ),
    "tone_optimizer": (
        "Tone Optimizer",
        "Improve clarity and audience fit without adding facts; return revised Markdown.",
    ),
    "publishing_coordinator": (
        "Publishing Coordinator",
        "Prepare final customer-facing Markdown without internal review data.",
    ),
}


class AIProviderLLMAdapter(BaseLLM):
    """Adapter so CrewAI can use the app's existing AIProvider implementation."""

    def __init__(self, provider, model: str = "mock-provider"):
        super().__init__(model=model, temperature=0.15)
        self.provider = provider

    def _stringify_messages(self, messages):
        if isinstance(messages, str):
            return messages
        if isinstance(messages, (list, tuple)):
            parts = []
            for item in messages:
                if isinstance(item, dict):
                    content = item.get("content")
                    if content is not None:
                        parts.append(str(content))
                else:
                    parts.append(str(item))
            return "\n".join(parts)
        return str(messages)

    def call(
        self,
        messages,
        tools=None,
        callbacks=None,
        available_functions=None,
        from_task=None,
        from_agent=None,
        response_model=None,
        **kwargs,
    ):
        prompt = self._stringify_messages(messages)
        if not prompt:
            return ""

        provider = getattr(self, "provider", None)
        if provider is None or not hasattr(provider, "generate"):
            raise RuntimeError("CrewAI requires a configured AI provider with generate().")

        try:
            if asyncio.iscoroutinefunction(provider.generate):
                def _run_async():
                    return asyncio.run(
                        provider.generate(
                            "You are a careful technical writer. Produce customer-facing Markdown only.",
                            prompt,
                        )
                    )

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(_run_async)
                    return future.result()

            return provider.generate(
                "You are a careful technical writer. Produce customer-facing Markdown only.",
                prompt,
            )
        except Exception as exc:
            raise RuntimeError("CrewAI could not call the configured AI provider.") from exc


def build_crew(llm, task_inputs: dict[str, str]) -> Crew:
    """Build the CrewAI role pipeline with a caller-configured LLM."""
    if hasattr(llm, "generate") and not isinstance(llm, BaseLLM):
        llm = AIProviderLLMAdapter(llm)

    agents = {
        key: Agent(
            role=role,
            goal=goal,
            backstory="A specialist in governed, source-grounded documentation.",
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )
        for key, (role, goal) in ROLE_DETAILS.items()
    }
    task_specs = list(ROLE_DETAILS.items())
    tasks = []
    previous_tasks = []
    for key, (_, goal) in task_specs:
        task = Task(
            description=task_inputs.get(key, goal),
            expected_output=goal,
            agent=agents[key],
            context=previous_tasks.copy() or None,
        )
        tasks.append(task)
        previous_tasks.append(task)
    return Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=False,
    )
