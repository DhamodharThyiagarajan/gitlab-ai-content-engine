# Evaluation and quality metrics

This document defines the quality dimensions for generated content. The workflow currently calculates a heuristic score from unsupported claims, technical risks, context gaps, reviewer-discovered missing information, and the technical-review verdict.

## Metrics

- source coverage
- factual alignment
- rewrite count
- approval cycle time
- review rework rate
- tone consistency
- publication readiness

## Current validation

- Human review is required before export.
- Workflow output includes source references and risk flags.
- The heuristic score is stored on the content job and included in technical-review metadata; it is advisory, not a factuality guarantee.
- Prompt and extraction contracts are checked under `tests/ai_output_tests/` and `tests/functional_tests/`.

## Production follow-up

- Add source-coverage and factual-alignment scoring against the evidence pack.
- Store score versions and reviewer outcomes for longitudinal comparison.
- Keep automated scores advisory; retain human approval as the publication gate.
