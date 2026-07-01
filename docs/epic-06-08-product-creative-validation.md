# Epic 06-08 Product And Creative Validation

This document maps the Sprint 3 and Sprint 4 story batches to implemented Genesis runtime behavior.

## Epic 06 - Product Factory

US-00051 through US-00060 are implemented through `ProductDepartment.build_product_definition` and `ProductDepartment.execute_blueprint`.

- Product Department initialization is emitted as `departmentInitialization`.
- EMP-101 Product Manager assignment is emitted as `productManager`.
- Product strategy is emitted as `productStrategy`.
- Product specification is emitted as `productSpecification`.
- Product variants and roadmap are emitted as `variantMatrix`, `productVariants`, and `productRoadmap`.
- Manufacturability, manufacturing method, material recommendations, product architecture, and concept validation are emitted as first-class blueprint sections.
- Product concept validation must approve progression to Product Blueprint.

## Epic 07 - Product Engineering And Commercialization

US-00061 through US-00070 are implemented by EMP-101 through EMP-110 and the final Product Blueprint assembler.

- BOM includes component identifiers, quantities, material mapping, unit costs, supplier categories, alternatives, and notes.
- Cost analysis includes raw material, manufacturing, assembly, packaging, labels, shipping, warehousing, marketplace fees, taxes, returns, buffers, assumptions, and sensitivity analysis.
- Supplier intelligence includes shortlist, location, product range, pricing estimate, quality indicators, capacity, MOQ, lead time, risks, and linked BOM items.
- Packaging includes primary and secondary packaging, inserts, labels, barcodes, QR codes, storage, branding requirements, sustainability, and estimated cost.
- Shipping readiness is emitted as `shippingAssessment`.
- Quality assessment includes failure modes, assembly, material, durability, safety, customer experience risks, and inspection recommendations.
- Profitability includes selling price, wholesale price, marketplace price, gross margin, net margin, break-even, ROI, rating, scalability, inventory risk, and assumptions.
- Product Review Gate is emitted as `productReviewGate` and must approve Creative Studio handoff.
- Completion, validation history, founder notification, and Creative Studio transition are persisted in the blueprint.

## Epic 08 - Creative Studio

US-00071 through US-00080 are implemented by `CreativeDepartment` and EMP-201 through EMP-210.

- Creative Studio initialization is emitted as `creativeStudio`.
- Creative Director assignment is emitted as `creativeDirector`.
- Creative execution plan is emitted as `creativeExecutionPlan`.
- Brand context and approved Product Blueprint precondition are emitted before creative work.
- Brand strategy, naming, identity, logo system, visual identity, packaging design, mockups, marketplace assets, social assets, launch copy, and QA are generated.
- Brand guidelines are emitted as `brandGuidelinesDocument`, including logo, colors, typography, spacing, imagery, illustration, iconography, tone, copy, accessibility, do, and don't rules.
- Creative validation is emitted as `creativeValidationReport` with validation areas, warnings, error list, blocked-failed-assets policy, and validation history.
- Marketing handoff is emitted as `marketingTransition`.
- Knowledge entries record creative system and asset-generation lessons.

## Implemented Beyond The Story Text

Sprint 4 now generates deterministic binary asset files through `apps.creative.assets`:

- SVG logo files.
- PNG placeholder/product creative files.
- PDF handoff-style files.

OpenAI image generation can be enabled later through provider credentials, but deterministic local generation is already covered by tests so the workflow is executable without external services.

## Verification

The following checks enforce this story coverage:

- `scripts/validate_product_definition.py`
- `scripts/validate_product_blueprint.py`
- `scripts/validate_creative_pack.py`
- `tests/test_product_department.py`
- `tests/test_product_blueprint.py`
- `tests/test_creative_pack.py`
