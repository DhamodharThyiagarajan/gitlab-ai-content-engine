# Audit log export

## Release

Release: 2.4.0
Availability date: 2026-09-15

## Changes

- Project Maintainers can export audit events as a CSV file from **Settings > Audit events**.
- Each export includes the event timestamp, actor, action, and target resource.
- Exports are limited to the selected date range and the current project.
- Only users with the Maintainer role can create an export.

## Limitations

- Exports are generated on demand and are not emailed to users.
- Events older than 365 days are not available in the export.

## Support

Contact the project administrator if the export action is unavailable.