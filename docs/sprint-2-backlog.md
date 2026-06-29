# Sprint 2 Engineering Backlog

Version: 0.1.0
Sprint: 1D handoff to Sprint 2
Status: Ready for Sprint 2 execution

## Sprint 2 goal

Build the first working AI Product Factory MVP that converts a founder text requirement into a complete launch pack.

## Epics

### EPIC-001 Product Factory Runner

Create the core runner that accepts founder input and produces structured output.

User stories:

- As a founder, I can submit a plain-text product/store requirement.
- As Genesis Orchestrator, I can route the request to the right AI employee sequence.
- As a founder, I can receive a launch pack that follows the schema.

Tasks:

- Create manual runner flow.
- Map each output section to schema fields.
- Add one complete example launch pack.
- Add validation checklist.

Acceptance criteria:

- One text requirement produces research, product, creative, marketing, publishing, and validation sections.
- Output references assumptions and risks.
- Phase 1 and Phase 2 steps are separated.

Priority: P0
Dependencies: Sprint 1D schemas and prompts

### EPIC-002 Launch Pack Schema Validation

Validate that generated launch packs follow the committed schema.

User stories:

- As an engineer, I can validate output JSON against schema.
- As a founder, I can trust that every launch pack has the same structure.

Tasks:

- Create example valid launch pack.
- Add schema validation command.
- Extend CI to include launch pack fixture.

Acceptance criteria:

- Fixture parses as valid JSON.
- Required launch-pack sections are present.

Priority: P0
Dependencies: `schemas/launch-pack.schema.json`

### EPIC-003 Manual Launch Operations

Create a manual operating system for launching without Meta API, Supabase, VPS, or Cloudflare.

User stories:

- As a founder, I can launch manually from the generated pack.
- As a founder, I know exactly what to post, where to collect leads, and how to track orders.

Tasks:

- Create manual launch checklist.
- Create lead tracker template.
- Create first 7-day validation scorecard.

Acceptance criteria:

- Manual workflow can be executed without paid infrastructure.
- Every step has an owner and output.

Priority: P1
Dependencies: Product Factory Runner

### EPIC-004 AI Employee Test Cases

Create regression tests for every AI employee.

User stories:

- As an engineer, I can compare prompt output across versions.
- As a founder, I can see quality does not silently degrade.

Tasks:

- Add input cases for GENESIS-ORCH, EMP-001, EMP-002, EMP-003, EMP-004.
- Define expected output sections.
- Add fixture outputs.

Acceptance criteria:

- Every employee has at least one regression case.
- Expected sections are documented.

Priority: P1
Dependencies: AI workforce prompt library

### EPIC-005 Future Automation Hooks

Prepare Phase 2 without building paid infrastructure yet.

User stories:

- As Genesis AI, I can mark which steps are manual now and automatable later.
- As founder, I can see what Supabase, Meta API, VPS, and Cloudflare will add later.

Tasks:

- Create automation hook registry.
- Add platform dependency notes.
- Add Phase 2 cost/infra assumptions.

Acceptance criteria:

- Every manual step has optional automation mapping.
- No Phase 1 step depends on unavailable paid infrastructure.

Priority: P2
Dependencies: Manual Launch Operations

## Sprint 2 priorities

1. P0: Product Factory Runner
2. P0: Launch Pack Schema Validation
3. P1: Manual Launch Operations
4. P1: AI Employee Test Cases
5. P2: Future Automation Hooks

## Sprint 2 done criteria

Sprint 2 is complete when a founder can paste one product requirement and receive a complete, repeatable, schema-aligned launch pack that can be executed manually within 1 to 3 days.
