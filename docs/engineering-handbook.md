# Genesis AI Engineering Handbook

From this point onward, Genesis AI is a product, not just a conversation. Every decision we make should contribute to a real, buildable system.

## Genesis AI v1 Roadmap

### Phase 1 — Research Department

Goal: Decide what to build.

Employees:

- Trend Research AI
- Competitor Research AI
- Customer Research AI
- Product Research AI

Output: Research Report

### Phase 2 — Product Department

Goal: Decide how to build it.

Employees:

- Product Planner
- Pricing Expert
- POD Expert

Output: Product Blueprint

### Phase 3 — Creative Department

Goal: Create assets.

Employees:

- Creative Director
- Design Generator
- Mockup Generator

Output: Design Pack

### Phase 4 — Marketing Department

Goal: Sell the products.

Employees:

- Instagram Manager
- Facebook Manager
- Copywriter
- SEO Writer

Output: Marketing Pack

### Phase 5 — Publishing Department

Goal: Publish everywhere.

Initially:

- Qikink
- Instagram
- Facebook

Later:

- Amazon
- Shopify
- Etsy

### Phase 6 — Analytics Department

Goal: Learn from results.

Outputs:

- Best-selling niches
- Best-performing designs
- Winning colors
- Winning products
- Recommendations for the next cycle

## Development Rules

These are the engineering rules we'll follow throughout Genesis:

- Manual first, automation second.
- Every employee has one responsibility.
- Every decision must be backed by data when possible.
- Every output is stored for future learning.
- No vendor lock-in. Qikink is the first provider, not the only one.

## Sprint 1 Deliverable

By the end of this sprint, Genesis should be able to do this:

Input:

```text
Build a business around coffee lovers.
```

Output:

- Market research report
- Competition summary
- Recommended products
- Product concepts
- Design prompts
- Titles and descriptions
- Social media captions
- Ready-to-review package

No coding is required yet. We are validating the workflow and the quality of each employee.

## Product Mindset

Genesis should not become a collection of prompts.

Genesis should become a digital company.

When someone asks in the future:

```text
Who designed this product?
```

The answer should not be:

```text
ChatGPT
```

It should be:

```text
Creative Department - Genesis AI
```

When someone asks:

```text
Who decided to enter this niche?
```

The answer should be:

```text
Research Department - Genesis AI
```

That mindset keeps the architecture clean and makes it much easier to automate department by department.

## Sprint 2 Remaining Work

### Real Marketplace APIs

Current implementation uses targeted live search, such as Amazon pages and Instagram pages, rather than official APIs.

Still needed:

- Amazon Product Advertising API
- Shopify Storefront/Admin API
- Etsy API
- Meta Graph API for Instagram/Facebook
- YouTube Data API
- Google Trends API

Status: Functional but not official integrations.

### Search Aggregation Engine

Instead of each employee searching independently:

```text
EMP1 -> Search
EMP2 -> Search
EMP3 -> Search
EMP4 -> Search
```

Build:

```text
Search Manager
  -> One unified search
  -> Cache
  -> Employees reuse results
```

Benefits:

- Faster
- Lower API usage
- Better consistency

Status: Pending.

### Confidence Engine

Research confidence should be calculated from:

- Number of sources
- Source diversity
- Agreement between sources
- Freshness
- Data completeness

Status: Pending.

### Citation Engine

Every recommendation should include citations such as:

- Amazon listing
- Instagram page
- Competitor website
- News article
- Trend source

Status: Partial.

### Research Memory

Avoid repeating searches.

Need:

```text
Research Cache
  -> Embeddings
  -> Similarity Search
  -> Reuse previous research
```

Status: Pending.

### Cost Tracking

Track:

- OpenAI tokens
- API costs
- Search requests
- Runtime
- Per employee

Status: Pending.

### Observability

Need dashboards for:

- Workflow duration
- Employee runtime
- Errors
- API latency

Status: Pending.

### Parallel Employee Execution

Currently employees execute sequentially.

Need:

```text
EMP1
EMP2
EMP3
EMP4
  -> Run simultaneously
```

This will significantly reduce runtime.

Status: Pending.

### Retry and Recovery

Need:

- Automatic retries
- Backoff
- Resume interrupted workflows

Status: Basic workflow retry exists; comprehensive recovery does not.

### Approval Workflow

Support:

- Auto
- Manual
- Human approval

Approval should happen before proceeding to later departments.

Status: Pending.

## Sprint Split Recommendation

Do not close Sprint 2 yet. Split the remaining work into three implementation phases.

### Sprint 2A — Runtime

Status: Approximately 95% complete.

Completed:

- Core runtime
- Workflow
- Research
- API
- Live web
- Marketplace search

### Sprint 2B — Intelligence

Scope:

- Confidence engine
- Citation engine
- Search aggregation
- Research cache
- Parallel execution

### Sprint 2C — Production Readiness

Scope:

- Official marketplace/API integrations
- Cost tracking
- Observability
- Approval workflow
- End-to-end validation
- CI verification

## Completion Snapshot

Based on the agreed Sprint 2 scope:

- Core platform: 100%
- Live research capability: 85-90%
- Production-grade intelligence: approximately 60%
- Overall Sprint 2: approximately 85% complete

The remaining work turns a functioning research engine into a production-ready, scalable intelligence platform.
