# AI Workflow States

A content job moves through the following states during the AI documentation lifecycle.

## State Table

| Status                   | Meaning                                                                                    | Set by                 |
| ------------------------ | ------------------------------------------------------------------------------------------ | ---------------------- |
| `uploaded`               | Source document has been uploaded and is ready for processing                              | Content Intake         |
| `reading`                | Context Reader extracts technical context and retrieves relevant supporting knowledge      | Context Reader         |
| `writing`                | Documentation Writer generates the first documentation draft                               | Documentation Writer   |
| `fact_checking`          | Fact Checker verifies the draft against the uploaded source                                | Fact Checker           |
| `tone_editing`           | Tone Editor improves clarity and audience-appropriate tone without changing verified facts | Tone Editor            |
| `ready_for_human_review` | AI workflow is complete and the draft is waiting for human approval                        | AI Workflow            |
| `approved`               | Human reviewer has approved the documentation                                              | Human Reviewer         |
| `revision_requested`     | Human reviewer has rejected the draft and requested changes                                | Human Reviewer         |
| `publishing`             | Approved content is being prepared for publication                                         | Publishing Coordinator |
| `published`              | Final documentation has been generated as Markdown                                         | Publishing Coordinator |
| `failed`                 | The workflow encountered an execution or processing error                                  | AI Workflow            |

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
   ├── APPROVE → approved
   │                  │
   │                  ▼
   │              publishing
   │                  │
   │                  ▼
   │              published
   │
   └── REJECT → revision_requested
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
```

## Workflow Notes

* The uploaded document is the **primary source of truth** for the AI workflow.

* During `reading`, the **Context Reader** extracts the relevant technical context from the uploaded document.

* The Context Reader can also retrieve supporting information from **Chroma**, such as style guides, sample documentation, and content templates.

* Chroma provides supporting context and does **not** replace the uploaded source.

* The **Documentation Writer** uses the verified context to generate the initial documentation draft.

* The **Fact Checker** verifies the generated claims against the uploaded source and identifies unsupported or incorrect information.

* The **Tone Editor** improves clarity, structure, and audience-appropriate tone while preserving verified technical information.

* `ready_for_human_review` is a **mandatory human checkpoint**. Content is not published automatically after the AI workflow.

* If the reviewer **approves** the draft, the workflow moves to `approved` and then `publishing`.

* If the reviewer **rejects** the draft, the workflow moves to `revision_requested`. The reviewer's feedback is sent back to the Documentation Writer.

* After revision, the content passes through **Writer → Fact Checker → Tone Editor → Human Review** again.

* Previous versions can be retained so that revisions and review decisions are traceable.

* `published` is the final state in the current MVP.

* The **Publishing Coordinator** prepares the approved documentation as a **Markdown export**.

* `failed` represents an **AI or system execution error** and is separate from a human-requested revision.
