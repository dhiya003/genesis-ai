# Sprint 2 Plan — Research Department Vertical Slice

## Goal

Build the first working Genesis workflow: Founder niche input → Genesis project → Research workflow → Trend Report → Founder review.

## Scope

Sprint 2 focuses only on the first vertical slice.

Included:

- Project creation
- Workflow creation
- Trend Research Specialist execution
- Trend Report storage
- Report retrieval
- Manual founder review

Excluded:

- Full competitor research
- Full customer research
- Full product research
- Product Department
- Creative Department
- Marketing Department
- Automated publishing

## Deliverables

1. Project service
2. Workflow service
3. Report service
4. Trend Research runner
5. CLI or minimal API endpoint
6. Database persistence
7. Sample trend report generation
8. Test fixtures

## Acceptance Criteria

Given a niche such as `Coffee Lovers`, Genesis must:

1. Create a project record.
2. Create a research workflow.
3. Execute the Trend Research Specialist prompt.
4. Produce a structured Trend Report.
5. Store the report.
6. Retrieve the report by ID.

## Definition of Done

- Local database runs through Docker Compose.
- Schema is applied successfully.
- Seed data loads successfully.
- Trend Research Specialist prompt is available.
- Sample project fixture exists.
- Research output validates against schema.
- README includes local run instructions.
