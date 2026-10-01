# Retrieval and knowledge layer

This directory records the knowledge-retrieval design boundary. The current runtime does not query a vector store or retrieve prior approved documents; each job is grounded in the source material provided with that job.

## Planned responsibilities

- Search prior documentation and approved examples
- Store reusable GitLab voice guidance
- Retrieve product terminology and templates
- Surface stale, conflicting, or missing evidence
- Support grounded content generation before drafting

## Production follow-up

- Select a vector store only after defining tenant isolation, source retention, and deletion behavior.
- Store chunk metadata with source references, owner, timestamps, and access scope.
- Add retrieval only as supplemental context; never replace the current job's authoritative source material.
- Add relevance and access-control tests before connecting retrieval results to generation.
