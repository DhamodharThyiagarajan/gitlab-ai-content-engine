
from pathlib import Path


def test_ai_workflow_file_exists():
    workflow_file = Path("backend/ai/workflow.py")

    assert workflow_file.exists()
    assert workflow_file.is_file()


def test_ai_workflow_contains_expected_agents():
    workflow_file = Path("backend/ai/workflow.py")
    content = workflow_file.read_text(encoding="utf-8")

    expected_agents = [
        "context_reader",
        "documentation_writer",
        "technical_reviewer",
        "tone_optimizer",
        "publishing_coordinator",
    ]

    for agent in expected_agents:
        assert agent in content


def test_ai_workflow_contains_crewai():
    workflow_file = Path("backend/ai/workflow.py")
    content = workflow_file.read_text(encoding="utf-8")

    assert "crewai" in content.lower()
