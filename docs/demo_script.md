# Demo

1. Sign in as `writer@example.com` / `password123`.
2. Create a new release-note content job and provide the source text.
3. Run the AI workflow and show the generated draft, source information, and risk flags.
4. Sign in as `reviewer@example.com` and review the generated draft.
5. Request revisions if changes are required, or proceed with approval through an approver/admin account.
6. After approval, export the final documentation as Markdown using `POST /api/publish/export`.
7. Open the Operations dashboard and show the available workflow and system metrics.
