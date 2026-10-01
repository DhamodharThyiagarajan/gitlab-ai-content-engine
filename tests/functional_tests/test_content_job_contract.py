from pathlib import Path


def test_project_contract_for_spec_sections():
    root = Path(__file__).resolve().parents[2]

    required_directories = [
        "frontend/src/app",
        "frontend/src/components",
        "frontend/content-editor",
        "frontend/review-panel",
        "frontend/styles",
        "backend/api",
        "backend/auth",
        "backend/services",
        "backend/orchestration",
        "backend/database",
        "backend/publishing",
        "backend/app/api",
        "backend/app/auth",
        "backend/app/services",
        "backend/app/orchestration",
        "backend/app/db",
        "ai/agents/context_reader",
        "ai/agents/documentation_writer",
        "ai/agents/technical_reviewer",
        "ai/agents/tone_optimizer",
        "ai/agents/publishing_coordinator",
        "ai/prompts",
        "ai/schemas",
        "ai/retrieval",
        "ai/evaluation",
        "data/sample_inputs",
        "data/sample_docs",
        "data/style_guides",
        "data/content_templates",
        "docs/screenshots",
        "tests/functional_tests",
        "tests/ai_output_tests",
        "tests/security_tests",
        "tests/edge_cases",
        "deployment",
    ]
    assert all((root / directory).is_dir() for directory in required_directories)
    assert (root / "backend" / "app" / "main.py").exists()
    assert (root / "frontend" / "src" / "app" / "create-content" / "page.js").exists()
    assert (root / "ai" / "README.md").exists()
    assert (root / "data" / "sample_inputs").exists()
    assert (root / "deployment" / "README.md").exists()
