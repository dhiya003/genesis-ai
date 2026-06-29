# Sprint 3 Phase 1 - Product Definition

Release: v0.3.0
Department: Product Department
Status: Implementation specification

## Purpose

Phase 1 converts a validated Sprint 2 Research Report into a real product direction.

Input:

```text
Research Report
```

Output:

```text
Product Definition
```

## Product Definition Engine

The Product Definition Engine transforms research into an actual product that can later be engineered, manufactured, packaged, costed, and sourced.

It must answer:

- Product name
- Category
- Purpose
- Problem solved
- Target customer
- Age group
- Use case
- Product story
- Differentiator
- Variants
- Future roadmap

## Product Definition Document

The Product Definition Document is the first Product Department deliverable.

Required fields:

- `projectId`
- `sourceReportId`
- `productName`
- `category`
- `purpose`
- `problemSolved`
- `targetCustomer`
- `ageGroup`
- `useCase`
- `productStory`
- `differentiator`
- `educationalDomain`
- `recommendedMaterial`
- `difficulty`
- `packagingType`
- `variants`
- `futureRoadmap`
- `evidence`
- `assumptions`

Example:

```text
Name: Luma Logic Cubes
Purpose: Teach children logical reasoning.
Age: 3-5 years
Material: Beech wood
Difficulty: Easy
Educational Domain: Logic, motor skills, pattern recognition
Packaging: Starter Kit
```

## Product Opportunity Ranking

Genesis must evaluate each product opportunity using 0-100 scores.

Scored dimensions:

- Customer Value
- Market Gap
- Competition
- Manufacturing Difficulty
- Profit
- Differentiation
- Scalability
- Supplier Availability
- Inventory Risk
- Shipping Risk
- Learning Value

The ranking output must include:

- Score per dimension
- Overall Opportunity Score
- Ranking rationale
- Rejection reasons for weak alternatives
- Evidence references from the research report

## Product Variants

Genesis should not create a single-product dead end. It must design the product as a family.

Required variant levels:

- Starter
- Standard
- Premium
- Bundle
- Subscription
- Accessories
- Expansion Packs

Example for an educational toy:

```text
Starter: 6 cubes
Standard: 12 cubes
Premium: 24 cubes
Teacher Kit
Classroom Kit
Replacement Parts
```

## Product Roadmap

Every product needs a roadmap.

Required roadmap sections:

- Version 1
- Version 2
- Version 3
- Future features
- Accessories
- Digital companion
- Subscription
- Expansion opportunities

## Product Validation Questions

The Product Manager must validate:

- Does it solve a real problem?
- Can parents or buyers understand it quickly?
- Can it be manufactured?
- Can it be shipped?
- Can it scale?
- Can it be branded?
- Can it become a product family?

## Product Constraints

Genesis must consider:

- Founder budget
- Manufacturing capability
- Country
- Minimum order quantity
- Machine availability
- Shipping
- Storage
- Safety
- Target margin
- Time to market

## Product Engineering Rules

Every product must be:

- Unique
- Profitable
- Simple
- Easy to manufacture
- Easy to package
- Easy to ship
- Easy to scale
- Easy to explain
- Easy to market

## Product Metrics

Genesis calculates:

- Complexity Score
- Manufacturability Score
- Innovation Score
- Profitability Score
- Customer Value Score
- Shipping Score
- Packaging Score
- Expansion Potential
- Overall Product Score

## Product Knowledge Base

Genesis must store:

- Every generated product
- Every rejected product
- Reason for rejection
- Alternative designs
- Lessons learned
- Future improvements

This becomes institutional product intelligence.

## Phase 1 deliverables

At the end of Product Definition, Genesis must generate:

1. Product Definition Document
2. Product Opportunity Report
3. Product Variant Matrix
4. Product Roadmap
5. Product Constraints Report
6. Product Success Metrics
7. Product Risk Register
8. Product Approval Checklist

## Acceptance criteria

Phase 1 is complete when:

- A stored Research Report can be used as the input.
- Product Department creates a Product Definition workflow.
- Product Manager evaluates at least one product opportunity.
- Product variants include starter, standard, premium, bundle, subscription, accessories, and expansion packs.
- Opportunity and product metrics include 0-100 scores.
- Rejected alternatives and rejection reasons are persisted.
- All eight Phase 1 deliverables are stored and retrievable.
- Product Knowledge Base entries are written.
- API and CLI can retrieve the Product Definition outputs.
- Tests and CI pass.
