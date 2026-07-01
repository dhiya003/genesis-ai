# Genesis v1 Epic 02-04 Lifecycle Validation

This document records the implementation status for the attached Genesis v1 story batches:

- Epic 02 Project Lifecycle, US-00011 to US-00020
- Epic 03 Workflow Lifecycle, US-00021 to US-00030
- Epic 04 Research Department, US-00031 to US-00040

## Epic 02 Project Lifecycle

Implemented in `apps/project/lifecycle.py`.

- Project dashboard with project name, current phase, completion percentage, active workflow, assigned departments, pending approvals, health, activities, deliverables, risks, recommendations, timeline, KPIs, and on-demand refresh metadata.
- Project update with editable-field validation, project version snapshots, and audit logging.
- Archive and restore with timestamps, preserved reports/workflows/deliverables, and audit logging.
- Duplicate project with a new project ID, source linkage, copied configuration, retained owner, and no copied workflow/report/audit history.
- Chronological immutable timeline assembled from audit and execution history with JSON export metadata.
- Project status validation and transition protection for terminal states.
- Project health score from research, timeline, budget, risk, deliverables, workflow success, pending issues, and approvals, with persisted trend snapshots.
- Project audit trail via the existing immutable audit store.
- Readiness validation report covering business, vision, goals, constraints, budget, approval policy, founder profile, status, and required project fields. Blocking failures prevent planning.

## Epic 03 Workflow Lifecycle

Implemented in `apps/workflow/engine.py`.

- Workflow creation now includes globally unique ID, project link, best-effort business link, name, type, creator, priority, version, current stage, progress, idempotency key, creation timestamp, audit, execution event, and notification.
- State machine includes `NEW`, `VALIDATING`, `PLANNING`, `READY`, `RUNNING`, `WAITING`, `APPROVAL_REQUIRED`, `RESUMING`, `COMPLETED`, `FAILED`, `RETRYING`, `CANCELLED`, and `ARCHIVED`.
- Invalid workflow transitions are rejected and valid transitions are recorded in immutable state history.
- Pause, resume, retry, cancel, completion, and failure preserve history and publish audit/execution/notification records.
- Progress view exposes current phase, department, employee, completed/remaining tasks, elapsed time, progress percentage, warnings, blocking issues, outputs, and deliverables.
- History view exposes state history, execution history, employees, deliverables, approvals, and notifications.
- Notifications are timestamped, persisted, configurable by policy in future integrations, and deduplicated by workflow/event/status/attempt.

## Epic 04 Research Department

Already implemented before this pass in `apps/research/department.py`, `apps/employees/research.py`, and `apps/orchestrator/genesis_orchestrator.py`.

- Research Department executes EMP-001 to EMP-004 end-to-end.
- Research manager behavior is represented by department orchestration, execution plan generation, employee sequencing, output validation, and report merge.
- Employee outputs include evidence, confidence, validation, metrics, retry policy, timeout, and prompt contract metadata.
- Combined research report includes trend analysis, competitor analysis, customer analysis, product research, score, recommendation, risks, next actions, evidence, and confidence.
- Report is persisted, linked to project/workflow, retrievable through API/CLI, and validated by `scripts/validate_research_report.py`.

## Implemented Extras For Review

The current codebase also exposes downstream deliverables in project dashboards when available: product knowledge, execution history, deliverables, approvals, and department output references. These were not explicitly required by the Epic 02 dashboard story, but are useful for founder review and governance.

## Tests

Story coverage is verified by:

- `tests/test_project_lifecycle.py`
- `tests/test_workflow_engine.py`
- `tests/test_research_department.py`
- `tests/test_founder_management.py`
