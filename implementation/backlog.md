# Genesis AI Implementation Backlog

## Sprint 1D - Engineering Design Pack

### EDP-01 Physical Database Design
- [x] Initial PostgreSQL schema
- [x] Initial ER diagram
- [ ] Add seed data for departments and employees
- [ ] Add migration directory structure
- [ ] Add SQL validation workflow

### EDP-02 API Contracts
- [x] Initial OpenAPI contract
- [ ] Add research report schema
- [ ] Add product blueprint schema
- [ ] Add creative pack schema
- [ ] Add marketing pack schema
- [ ] Add publishing package schema

### EDP-03 Architecture Diagrams
- [x] System context diagram
- [x] Research sequence diagram
- [x] Project state machine
- [ ] Add container diagram
- [ ] Add workflow state machine
- [ ] Add publishing sequence diagram

### EDP-04 Prompt Assets
- [x] Trend Research Specialist prompt
- [ ] Competitor Research Specialist prompt
- [ ] Customer Research Specialist prompt
- [ ] Product Research Specialist prompt
- [ ] Genesis Orchestrator prompt

### EDP-05 Testing Assets
- [x] Initial prompt regression dataset
- [ ] Add schema validation tests
- [ ] Add expected output fixtures
- [ ] Add prompt evaluation checklist

### EDP-06 Infrastructure
- [x] Docker Compose for local PostgreSQL
- [x] Environment template
- [x] Initial CI workflow
- [ ] Add local setup guide
- [ ] Add database reset script

## Sprint 2 - Research Department Implementation

### Goal
Implement the first working Genesis workflow: founder niche input to Trend Report.

### Tasks
- [ ] Create project model
- [ ] Create workflow model
- [ ] Create report model
- [ ] Implement Genesis Orchestrator skeleton
- [ ] Implement Trend Research Specialist runner
- [ ] Store generated Trend Report
- [ ] Add manual founder review flow
- [ ] Add CLI or minimal API endpoint for project creation

## Definition of Done for Sprint 2

Founder can submit a niche and Genesis can produce, store, and retrieve a structured Trend Report.
