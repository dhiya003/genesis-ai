# Sprint 3 Kickoff - Product Factory

Release: v0.3.0
Status: In implementation

## Sprint 3 mission

Convert Research Intelligence into Production Intelligence.

Sprint 2 answers:

```text
Should we build this business?
```

Sprint 3 answers:

```text
What exactly should we build?
```

Sprint 3 is the Product Factory sprint. It is responsible for converting a validated opportunity into a complete Product Blueprint that can support real manufacturer or supplier discussions.

## Business goal

After Sprint 3, the founder should have everything required before spending money:

- Exact product
- Product variants
- Manufacturing plan
- Material selection
- Bill of materials
- Packaging plan
- Cost model
- Profitability model
- Supplier shortlist
- Product Blueprint

## High-level workflow

```text
Research Report
    -> Product Department
    -> Product Planning
    -> Engineering
    -> Manufacturing
    -> Costing
    -> Packaging
    -> Supplier Selection
    -> Profitability
    -> Product Blueprint
```

## Sprint 3 department

Sprint 3 introduces the Product Department and supporting product factory capabilities across engineering, manufacturing, costing, packaging, supplier intelligence, and profitability.

The Product Department designs products that are:

- Manufacturable
- Profitable
- Differentiated
- Scalable

The Product Department owns every engineering decision between a validated opportunity and the final Product Blueprint.

## Product Director and employees

The Product Director is the department head for Sprint 3. The Product Director orchestrates:

- EMP-101 Product Manager
- EMP-102 Industrial Designer
- EMP-103 Manufacturing Engineer
- EMP-104 Material Engineer
- EMP-105 BOM Engineer
- EMP-106 Cost Engineer
- EMP-107 Packaging Engineer
- EMP-108 Supplier Analyst
- EMP-109 Quality Engineer
- EMP-110 Profitability Analyst

Department-head responsibilities:

- Read the Sprint 2 research report.
- Identify the best product opportunity.
- Assign employee work.
- Validate every employee output.
- Approve the Product Blueprint.

## Product lifecycle

Every product must pass through this lifecycle:

```text
Idea
    -> Validation
    -> Product Definition
    -> Industrial Design
    -> Material Engineering
    -> Manufacturing Planning
    -> Cost Engineering
    -> Packaging
    -> Supplier Selection
    -> Profitability
    -> Blueprint Approval
```

No step is optional. Later phases may implement the steps incrementally, but the lifecycle contract must remain stable.

## Sprint 3 phases

### Phase 1: Product Definition

Transform a validated research opportunity into a concrete product definition, opportunity ranking, variant matrix, roadmap, constraints report, success metrics, risk register, and approval checklist.

### Phase 2: Industrial Design & Material Engineering

Define CAD readiness, dimensions, tolerances, materials, safety rules, manufacturability assumptions, and industrial design constraints.

### Phase 3: Manufacturing, BOM, Supplier Intelligence, Packaging, Shipping & Cost Engineering

Define manufacturing process, bill of materials, supplier shortlist, packaging, logistics, landed cost, target margin, and profitability model.

### Phase 4: Product Blueprint & Integration

Generate the final Product Blueprint and wire Product Department outputs into APIs, CLI, storage, workflow integration, validation, tests, CI, and Sprint 3 Definition of Done.

## Sprint 3 boundary

Sprint 3 does not deliver:

- Creative Studio
- Marketing Department
- Store creation
- Publishing automation
- Sales automation
- Analytics optimization loop
- Full AI Product Factory

Those depend on a standardized Product Blueprint and belong to later sprints.

## Sprint 3 release gate

Sprint 3 is complete only when:

- Product Department runs from a stored Sprint 2 research report.
- Product Department generates all Sprint 3 Product Blueprint deliverables.
- EMP-101 through EMP-110 are implemented and executable.
- Product Blueprint passes schema validation.
- API and CLI can create and retrieve Product Department outputs and Product Blueprint sections.
- Unit, integration, and e2e tests pass.
- CI is green.
- Sprint 3 docs are committed.

See [Sprint 3 Definition of Done](sprint-3-definition-of-done.md) for the authoritative exit criteria.
