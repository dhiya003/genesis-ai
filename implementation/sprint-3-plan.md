# Sprint 3 Implementation Plan - Product Intelligence & Engineering

Release: v0.3.0
Status: Phase 1 implemented locally; remaining phases required for Sprint 3 completion

## Goal

Implement the Product Department so Genesis can convert a validated Sprint 2 Research Report into a complete Product Blueprint detailed enough for a manufacturer or supplier to begin implementation discussions.

## Phase 1 scope

Phase 1 implements Product Definition. This phase is not the full Sprint 3 DoD.

Deliverables:

- Product Definition Document
- Product Opportunity Report
- Product Variant Matrix
- Product Roadmap
- Product Constraints Report
- Product Success Metrics
- Product Risk Register
- Product Approval Checklist

## Phase 1 epics

### EPIC-S3-001 Product Department Skeleton

Create the Product Department package and manager orchestration.

Tasks:

- Add `apps/product` package.
- Add Product Department manager.
- Add deterministic Product Intelligence provider.
- Add Product Manager validation step.
- Route Product Department execution from a stored Research Report.

Acceptance criteria:

- Product Department can run without external API credentials.
- Output is deterministic in tests.
- Department execution records workflow, task, audit, execution history, and deliverable entries.

Priority: P0

Status: Implemented locally in v0.3.0 initial slice.

### EPIC-S3-002 Product Definition Engine

Transform a Research Report into a Product Definition Document.

Tasks:

- Read validated research report fields.
- Select best opportunity.
- Generate product name, category, purpose, problem solved, target customer, age group, use case, story, differentiator, variants, and roadmap.
- Preserve evidence and assumptions.

Acceptance criteria:

- Product Definition Document contains all required fields.
- Missing or invalid research report input fails with a standard error.
- Output can be stored and retrieved.

Priority: P0

Status: Implemented locally in v0.3.0 initial slice.

### EPIC-S3-003 Opportunity Ranking & Product Metrics

Score each product opportunity.

Tasks:

- Add ranking dimensions with 0-100 scores.
- Add Overall Opportunity Score.
- Add product metrics with 0-100 scores.
- Add rejection reasons for weak alternatives.

Acceptance criteria:

- All ranking and metric fields are present.
- Scores are bounded between 0 and 100.
- At least one rejected alternative is persisted with a reason.

Priority: P0

Status: Implemented locally in v0.3.0 initial slice.

### EPIC-S3-004 Variants, Roadmap, Constraints, Risks, and Approval

Create the remaining Phase 1 deliverables.

Tasks:

- Add Product Variant Matrix.
- Add Product Roadmap.
- Add Product Constraints Report.
- Add Product Success Metrics.
- Add Product Risk Register.
- Add Product Approval Checklist.

Acceptance criteria:

- Variants include starter, standard, premium, bundle, subscription, accessories, and expansion packs.
- Constraints include budget, country, MOQ, manufacturing capability, shipping, storage, safety, margin, and time to market.
- Approval checklist validates problem clarity, manufacturability, shipping, scalability, branding, and product-family potential.

Priority: P0

Status: Implemented locally in v0.3.0 initial slice.

### EPIC-S3-005 Product Knowledge Base

Persist institutional product intelligence.

Tasks:

- Store generated products.
- Store rejected products.
- Store alternatives and rejection reasons.
- Store lessons learned and future improvements.

Acceptance criteria:

- Knowledge base entries are written during Product Department execution.
- Entries are retrievable for a project.
- Tests prove both generated and rejected products are persisted.

Priority: P1

Status: Implemented locally in v0.3.0 initial slice.

### EPIC-S3-006 API, CLI, Validation, and CI

Expose and verify Sprint 3 Phase 1.

Tasks:

- Add API endpoint to run Product Department from a project or report.
- Add API endpoint to retrieve Product Definition outputs.
- Add CLI command to run Product Department.
- Add CLI command to retrieve Product Definition outputs.
- Add JSON schema for Product Definition output.
- Add validation script.
- Add unit, integration, and e2e tests.
- Extend `scripts/verify.py`.

Acceptance criteria:

- API and CLI paths work end to end.
- Validation script passes against fixture data.
- `python3 scripts/verify.py` passes locally.
- GitHub Actions passes after push.

Priority: P0

Status: Implemented locally for Product Definition endpoints and validation. Full Product Blueprint endpoints remain.

## Remaining Sprint 3 epics

### EPIC-S3-007 Product Employee Contracts

Implement EMP-101 through EMP-110 as executable Product Department employees.

Acceptance criteria:

- Each employee has input schema, output schema, prompt contract, validation, logging, retry policy, timeout, and metrics.
- Employee outputs are persisted and auditable.
- Employee tests pass.

Priority: P0

### EPIC-S3-008 Engineering and Manufacturing Intelligence

Generate engineering specification and manufacturing plan.

Acceptance criteria:

- Product dimensions, materials, assembly method, manufacturing process, difficulty, tooling, safety, and production time are generated.
- Manufacturing technology, sequence, process flow, assumptions, expected yield, and risks are generated.
- Engineering and manufacturing validation gates pass.

Priority: P0

### EPIC-S3-009 Materials, BOM, Packaging, Supplier, Cost, Pricing, and Profitability

Generate all downstream Product Blueprint sections.

Acceptance criteria:

- Material recommendations include primary and alternative materials with comparison.
- BOM includes part numbers, quantities, material mapping, costs, and supplier categories.
- Packaging includes dimensions, materials, protection, shipping, storage, and sustainability.
- Supplier intelligence includes shortlist, comparison, country, MOQ, lead time, risk score, and alternatives.
- Cost engine calculates landed cost, margins, break-even quantity, and ROI estimate.
- Pricing engine recommends manufacturing, wholesale, distributor, retail, marketplace, premium, and bundle pricing.
- Profitability report includes profit per unit, percentage, margin score, scalability score, inventory risk, and cash-flow impact.

Priority: P0

### EPIC-S3-010 Product Blueprint Integration

Assemble and expose the final Product Blueprint.

Acceptance criteria:

- Product Blueprint contains every section listed in `docs/sprint-3-definition-of-done.md`.
- Persist Product Blueprint, BOM, Cost Report, Supplier Report, Packaging Report, Profitability Report, and Manufacturing Plan.
- Implement `POST /products/generate`.
- Implement `GET /products/{id}`.
- Implement `GET /products/{id}/blueprint`.
- Implement `GET /products/{id}/bom`.
- Implement `GET /products/{id}/cost`.
- Implement `GET /products/{id}/suppliers`.
- Implement `GET /products/{id}/profitability`.

Priority: P0

### EPIC-S3-011 Founder Acceptance Test

Add the founder acceptance test for the full Sprint 3 Product Blueprint.

Input:

```text
Build a premium educational wooden toy business for children aged 3-5 in India.
```

Acceptance criteria:

- Genesis produces a validated Product Blueprint.
- Product variants include Starter, Standard, and Premium.
- Manufacturing recommendations are present.
- Complete BOM is present.
- Material recommendations are present.
- Packaging specification is present.
- Supplier shortlist is present.
- Cost and pricing analysis is present.
- Profitability assessment is present.
- Risks and assumptions are present.
- Launch-ready engineering package is present.

Priority: P0

## Sprint 3 Definition of Done

Sprint 3 is complete when:

- Product Department consumes a Sprint 2 Research Report.
- EMP-101 through EMP-110 execute successfully.
- Product Department generates all Product Blueprint deliverables.
- Final Product Blueprint is schema-validated.
- API and CLI can run and retrieve Product Blueprint outputs.
- Product Knowledge Base persists generated and rejected products.
- Founder acceptance test passes.
- Local verification passes.
- GitHub Actions is green.
- Sprint 3 documentation is committed.
