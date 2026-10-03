# Demo script (about 5 minutes)

Prepare three Firebase accounts and set their roles (see `deployment/environment_setup.md`): a **writer**, a **reviewer**, and an **approver** (or admin).

1. **Writer: intake.** Sign in, open *Create Content*. Pick *API Documentation*, audience *Developers*, and upload `data/sample_inputs/api_change.txt` (or paste it). Submit.
2. **Workflow.** The agents run: context reader, documentation writer, technical reviewer, tone optimizer, publishing coordinator. Mention the context gap that is surfaced ("rate limit behaviour is not described").
3. **Review screen.** Show the generated draft, source references, supported facts, context gaps, unsupported claims and the quality score.
4. **Rerun one stage.** As reviewer: choose *Tone only*, add a comment, *Request Revision*. A new version appears. Use *Compare an earlier version* to show the diff. Optionally *Edit manually*.
5. **Governance.** Show that the reviewer cannot approve. Sign in as approver and *Approve*.
6. **Publish.** Choose *Markdown with front matter* (then repeat with *CMS JSON*) and Publish. Show the downloaded file.
7. **Operations.** Open *Analytics*/*Dashboard*: throughput, pipeline, quality, rework rate.
8. Repeat quickly with `release_notes.txt` (release note), `blog_brief.txt` (developer blog), `onboarding_update.txt` (onboarding guide). Optionally show `conflicting_notes.txt` to demonstrate safe handling of conflicting input.
