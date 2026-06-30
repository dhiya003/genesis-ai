# Genesis Sprint 5 - Marketing Engine Definition of Done

Release: v0.5.0

## Mission

Convert a Sprint 4 Creative Pack and Sprint 3 Product Blueprint into a complete Marketing Pack.

Sprint 4 answers: how should the business look and sound?

Sprint 5 answers: how should the business launch, attract customers, and convert demand?

## Functional DoD

Sprint 5 is complete when Genesis can automatically produce a complete Marketing Pack from a Creative Pack and Product Blueprint without human campaign planning work.

## Marketing Department

Implemented and executable:

- Marketing Department exists.
- Marketing Director orchestrates execution.
- Workflow integrates with Sprint 3 Product Blueprint and Sprint 4 Creative Pack.
- Marketing outputs are validated, persisted, and retrievable.

## Marketing Employees

The following employees must be implemented and executable:

- EMP-301 Marketing Strategist
- EMP-302 SEO Specialist
- EMP-303 Instagram Content Planner
- EMP-304 Paid Ads Specialist
- EMP-305 Marketplace Listing Specialist
- EMP-306 Landing Page Copywriter
- EMP-307 Email Campaign Specialist
- EMP-308 WhatsApp Campaign Specialist
- EMP-309 Influencer Strategist
- EMP-310 Launch Manager / QA

Each employee must include:

- Input schema
- Output schema
- Prompt contract
- Validation
- Logging/metrics
- Retry policy
- Timeout

## Marketing Pack

Final Marketing Pack contains:

- Marketing strategy
- Launch positioning
- Customer personas
- SEO keyword plan
- Marketplace listing copy
- Instagram calendar
- Facebook/Instagram ad concepts
- Google ad concepts
- Landing page copy
- Email campaign
- WhatsApp campaign
- Influencer strategy
- Hashtag plan
- Launch plan
- Campaign QA report
- Founder approval checklist
- Risks
- Assumptions
- Next actions

## APIs

Implemented:

- `POST /marketing/generate`
- `GET /marketing/{id}`
- `GET /marketing/{id}/strategy`
- `GET /marketing/{id}/seo`
- `GET /marketing/{id}/social`
- `GET /marketing/{id}/ads`
- `GET /marketing/{id}/listing`
- `GET /marketing/{id}/launch`

## Founder Acceptance Test

Input:

Create a complete launch marketing pack for the premium educational wooden toy business for children aged 3-5 in India.

Expected output:

- Marketing strategy
- SEO plan
- Instagram launch calendar
- Ad concepts
- Landing page copy
- Marketplace listing
- Email campaign
- WhatsApp campaign
- Influencer strategy
- Launch plan
- Marketing QA
- Founder approval checklist

## Non-Goals

Sprint 5 does not publish campaigns, schedule posts, spend ad budget, or require live platform credentials. The MVP produces deterministic campaign plans and copy-ready assets for founder approval.

