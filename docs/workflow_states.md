# AI Workflow States

A content job moves through a series of states during the AI documentation lifecycle, from source document upload to final Markdown publication.

## State Table

| **Status**               | **Meaning**                                                        | **Set by**             |
| ------------------------ | ------------------------------------------------------------------ | ---------------------- |
| `uploaded`               | Source document has been uploaded and is ready for processing      | Content Intake         |
| `reading`                | Technical context is extracted and supporting knowledge is retrieved | Context Reader      |
| `writing`                | The initial documentation draft is generated                       | Documentation Writer   |
| `fact_checking`          | Generated content is verified against the uploaded source          | Fact Checker           |
| `tone_editing`           | Clarity, structure, and audience-appropriate tone are improved      | Tone Editor            |
| `ready_for_human_review` | AI processing is complete and the draft is waiting for human review | AI Workflow          |
| `approved`               | The human reviewer has approved the documentation                  | Human Reviewer         |
| `revision_requested`     | The human reviewer has requested changes to the draft              | Human Reviewer         |
| `publishing`             | Approved content is being prepared for publication                 | Publishing Coordinator |
| `published`              | Final documentation has been generated as Markdown                 | Publishing Coordinator |
| `failed`                 | The workflow encountered an AI or system execution error            | AI Workflow            |

## State Diagram

```text
uploaded
   │
   ▼
reading
   │
   ▼
writing
   │
   ▼
fact_checking
   │
   ▼
tone_editing
   │
   ▼
ready_for_human_review
   │
   ├── APPROVE ──▶ approved
   │                   │
   │                   ▼
   │               publishing
   │                   │
   │                   ▼
   │                published
   │
   └── REQUEST REVISION ──▶ revision_requested
                                │
                                ▼
                             writing
                                │
                                ▼
                          fact_checking
                                │
                                ▼
                           tone_editing

## Workflow Notes
- The uploaded document is the primary source of truth for the AI workflow.
- During reading, the Context Reader extracts relevant technical context from the uploaded document.
- The Context Reader can also retrieve supporting information from Chroma, such as style guides, sample documentation, and content templates.
- Chroma provides supporting context and does not replace the uploaded source.
- During writing, the Documentation Writer uses the verified context to generate the initial documentation draft.
- During fact_checking, the Fact Checker verifies generated claims against the uploaded source and identifies unsupported or incorrect information.
- During tone_editing, the Tone Editor improves clarity, structure, and audience-appropriate tone while preserving verified technical information.
- ready_for_human_review is a mandatory human checkpoint. Content is not published automatically after the AI workflow.
- If the reviewer approves the draft, the workflow moves to approved and then publishing.
- If the reviewer requests changes, the workflow moves to revision_requested, and the feedback is sent back to the Documentation Writer.
- After revision, the content goes through Writer → Fact Checker → Tone Editor → Human Review again.
- Previous versions can be retained so that revisions and review decisions remain traceable.
- The Publishing Coordinator prepares approved documentation as a Markdown export.
- published is the final state in the current MVP.
- failed represents an AI or system execution error and is separate from a human-requested revision.
                                │
                                ▼
                     ready_for_human_review
