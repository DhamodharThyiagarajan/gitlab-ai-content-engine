from conftest import read_sample
from ai.common import ungrounded_claims
from ai.prompts import PROMPT_VERSION, get_prompt, style_guidance


def test_guard_flags_invented_version_path_and_metric():
    flags = ungrounded_claims("Fixed in 17.9. Use /api/v4/new. Supports 500 MB.", "Fixed in 17.5. Supports 50 MB.")
    joined = " ".join(flags)
    assert "17.9" in joined and "/api/v4/new" in joined and "500 MB" in joined


def test_guard_passes_grounded_text():
    assert ungrounded_claims("Supports 50 MB in 17.5", "Supports 50 MB in 17.5") == []


def test_draft_is_grounded_in_source(run_job):
    job = run_job(content_type="api_docs")
    content = job["drafts"][0]["content"]
    assert "/api/v4/projects/:id/widgets" in content
    assert "last_activity_at" in content
    assert job["drafts"][0]["technical_review"]["unsupported_claims"] == []


def test_gap_is_surfaced_not_hidden(run_job):
    job = run_job(source=read_sample("blog_brief.txt"), content_type="blog_post", title="Pipeline badges")
    review = job["drafts"][0]["technical_review"]
    assert review["context_gaps"], "open question about private projects must be reported"


def test_prompts_are_versioned_and_complete():
    assert PROMPT_VERSION == "v1"
    for name in ("context_reader", "documentation_writer", "technical_reviewer", "tone_optimizer", "publishing_coordinator"):
        assert len(get_prompt(name)) > 100


def test_style_guidance_per_content_type():
    assert "Deprecations" in style_guidance("release_notes")
    assert "Parameters" in style_guidance("api_docs")
    assert "GITLAB VOICE GUIDE" in style_guidance("blog_post")
