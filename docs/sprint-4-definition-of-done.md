# Genesis Sprint 4 - Creative Studio Definition of Done

Release: v0.4.0

## Mission

Convert a validated Sprint 3 Product Blueprint into a launch-ready Creative Pack.

Sprint 3 answers: what exactly should we build?

Sprint 4 answers: how should this product look, sound, and present itself to customers?

## Functional DoD

Sprint 4 is complete when Genesis can automatically produce a complete Creative Pack from a Product Blueprint without human creative planning work.

## Creative Department

Implemented and executable:

- Creative Department exists.
- Creative Director orchestrates execution.
- Workflow integrates with Sprint 3 Product Blueprint.
- Creative outputs are validated, persisted, and retrievable.

## Creative Employees

The following employees must be implemented and executable:

- EMP-201 Brand Strategist
- EMP-202 Naming Specialist
- EMP-203 Logo Designer
- EMP-204 Visual Identity Designer
- EMP-205 Packaging Designer
- EMP-206 Product Mockup Designer
- EMP-207 Marketplace Creative Designer
- EMP-208 Social Media Designer
- EMP-209 Copywriter
- EMP-210 Creative Director / QA

Each employee must include:

- Input schema
- Output schema
- Prompt contract
- Validation
- Logging/metrics
- Retry policy
- Timeout

## Creative Pack

Final Creative Pack contains:

- Brand strategy
- Brand name recommendation
- Brand positioning
- Tone of voice
- Logo system
- Color palette
- Typography system
- Visual identity rules
- Packaging design brief
- Product mockup brief
- Marketplace creative pack
- Social media creative pack
- Launch copy pack
- Creative QA report
- Founder approval checklist
- Risks
- Assumptions
- Next actions

## APIs

Implemented:

- `POST /creative/generate`
- `GET /creative/{id}`
- `GET /creative/{id}/brand`
- `GET /creative/{id}/packaging`
- `GET /creative/{id}/mockups`
- `GET /creative/{id}/marketplace`
- `GET /creative/{id}/social`
- `GET /creative/{id}/copy`

## Founder Acceptance Test

Input:

Create a complete creative identity and launch asset pack for the premium educational wooden toy business for children aged 3-5 in India.

Expected output:

- Brand name and positioning
- Logo direction
- Color palette
- Typography
- Packaging design brief
- Product mockup brief
- Instagram creatives
- Marketplace image concepts
- Launch copy
- Creative QA
- Founder approval checklist

## Non-Goals

Sprint 4 does not publish assets and does not require live Canva, Figma, or image-generation credentials. The MVP produces deterministic creative specifications and image-generation-ready briefs.

