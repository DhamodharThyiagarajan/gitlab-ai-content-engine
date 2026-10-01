# AI Module

This folder contains the agent and prompt layer for the GitLab AI Content & Documentation Engine.

The executable multi-stage workflow is implemented in `backend/app/orchestration/workflow.py`; prompt definitions and JSON contracts are maintained here. The role directories document each agent's responsibility and do not duplicate runtime Python classes.

## Responsibilities

- Context extraction and evidence mapping
- Draft writing
- Technical review and risk detection
- Tone optimization for target audience and channel
- Publishing coordination and export preparation

## Layout

- `agents/` contains role-specific workflow definitions
- `prompts/` contains versioned prompt definitions
- `schemas/` contains JSON schemas for structured output
- `retrieval/` documents the planned knowledge retrieval boundary; the live workflow currently grounds output in the source documents supplied to each job.
- `evaluation/` documents quality dimensions and is backed by the focused tests under `tests/ai_output_tests/`; a separate production scoring service is not currently wired in.
