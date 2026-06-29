# System Context and Workflow Diagrams

Version: 0.1.0
Sprint: 1D

## System Context

```mermaid
flowchart LR
  Founder[Founder] --> Genesis[Genesis AI]
  Genesis --> Research[Research AI]
  Genesis --> Product[Product AI]
  Genesis --> Creative[Creative AI]
  Genesis --> Marketing[Marketing AI]
  Genesis --> GitHub[(GitHub)]
  Genesis --> Postgres[(PostgreSQL)]
  Marketing --> Social[Instagram/Facebook Manual or API]
  Product --> Shopify[Shopify or Manual Website]
```

## C4 Context

```mermaid
flowchart TD
  User[Founder] --> System[Genesis AI Product Factory]
  System --> Repo[GitHub Repository]
  System --> DB[PostgreSQL]
  System --> LLM[LLM Provider]
  System --> Channels[Sales and Marketing Channels]
```

## C4 Container

```mermaid
flowchart TD
  Web[Founder Console] --> API[Genesis API]
  API --> Orchestrator[Genesis Orchestrator]
  Orchestrator --> Workers[AI Workforce]
  API --> DB[(PostgreSQL)]
  Workers --> Contracts[JSON Schemas]
```

## C4 Component

```mermaid
flowchart TD
  Orchestrator --> Emp001[EMP-001 Research]
  Orchestrator --> Emp002[EMP-002 Product]
  Orchestrator --> Emp003[EMP-003 Creative]
  Orchestrator --> Emp004[EMP-004 Marketing/Publishing]
  Emp001 --> ResearchReport[Research Report]
  Emp002 --> Blueprint[Product Blueprint]
  Emp003 --> CreativePack[Creative Pack]
  Emp004 --> MarketingPack[Marketing Pack]
  Emp004 --> PublishingPackage[Publishing Package]
```

## Project State Machine

```mermaid
stateDiagram-v2
  [*] --> draft
  draft --> researching
  researching --> blueprinting
  blueprinting --> creative_packaging
  creative_packaging --> marketing_packaging
  marketing_packaging --> publishing_ready
  publishing_ready --> published
  published --> analyzing
  analyzing --> archived
  researching --> failed
  blueprinting --> failed
  creative_packaging --> failed
  marketing_packaging --> failed
```

## Workflow State Machine

```mermaid
stateDiagram-v2
  [*] --> queued
  queued --> running
  running --> needs_review
  needs_review --> approved
  approved --> completed
  running --> failed
  needs_review --> cancelled
```

## Research Sequence

```mermaid
sequenceDiagram
  Founder->>Genesis: Submit product idea
  Genesis->>EMP001: Request market research
  EMP001->>Genesis: Research Report
  Genesis->>Founder: Review recommendation
```

## Product Sequence

```mermaid
sequenceDiagram
  Genesis->>EMP002: Send approved research
  EMP002->>Genesis: Product Blueprint
  Genesis->>Founder: Request approval
```

## Publishing Sequence

```mermaid
sequenceDiagram
  Genesis->>EMP003: Generate creative pack
  Genesis->>EMP004: Generate marketing and publishing pack
  EMP004->>Founder: Publishing checklist
  Founder->>Channel: Manual publish or Phase 2 automation
```
