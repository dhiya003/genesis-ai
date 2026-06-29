# Genesis AI Engineering Handbook

Version: 0.1.0
Status: Living handbook
Owner: Genesis AI Engineering

## Product Principle

Genesis AI is an AI product factory, not a prompt collection. The system should behave like a digital company where departments own decisions, employees own responsibilities, and every output can be reviewed, stored, improved, and reused.

## Operating Model

Genesis runs as departments connected by workflow gates.

1. Research Department decides what to build.
2. Product Department decides how to build it.
3. Creative Department creates product and marketing assets.
4. Marketing Department prepares selling material.
5. Publishing Department sends approved products to channels.
6. Analytics Department learns from market results and feeds the next cycle.

Each department must produce a structured artifact that can be validated independently before the next department starts.

## Engineering Rules

- Manual first, automation second.
- Every employee has one responsibility.
- Every department output must be persisted.
- Every recommendation should include evidence when possible.
- Every automated decision should expose confidence and citations.
- Every workflow transition that can affect spend, publishing, or production should support approval.
- No vendor lock-in. Qikink is the first provider, not the only provider.
- The deterministic provider must keep local development and CI usable without secrets.

## Runtime Standards

The runtime must support:

- Local execution through the CLI.
- HTTP execution through the API.
- File-backed persistence for local and CI workflows.
- Stable schemas for reports and launch artifacts.
- Retry and recovery for interrupted workflows.
- Observability for workflow duration, employee runtime, errors, and provider usage.

Runtime code should avoid mandatory paid services in early sprints. Optional integrations may depend on credentials, but the default path must remain runnable on a clean machine.

## Workflow Standards

Workflow state must be explicit:

- `CREATED`: workflow has been created but not started.
- `RUNNING`: workflow is actively executing.
- `COMPLETED`: workflow finished and stored its result.
- `FAILED`: workflow failed with a persisted error.

Recovery must preserve the original workflow ID and increment the attempt count. A workflow left in `RUNNING` can be resumed by marking it recoverable and running the department again. A `FAILED` workflow can be retried through the same recovery path.

## Approval Standards

Approval gates protect transitions between departments.

Supported modes:

- `auto`: system approval for local development and low-risk runs.
- `manual`: founder approval before the next department proceeds.
- `human`: explicit human review mode for production-like workflows.

Approval records must include the project, workflow, gate, mode, status, requester, timestamps, and decision metadata.

## Observability Standards

Genesis should record lightweight metrics without requiring an external dashboard in early sprints.

Minimum metric categories:

- workflow created, running, completed, failed, retried, recovered
- employee completed with runtime and score
- research report stored with overall score and confidence

Future production deployments can export the same events to a hosted dashboard without changing department logic.

## Research Standards

Research output must include:

- market or trend analysis
- competitor analysis
- customer analysis
- product research
- confidence
- citations
- risks
- next actions
- cost or usage summary

When official marketplace APIs are unavailable, live search may be used as a bridge, but the report must make the evidence level clear.

## Testing Standards

Every Sprint 2 runtime change should include focused tests for:

- workflow state changes
- persisted artifacts
- CLI behavior
- API behavior when applicable
- report schema validity when report output changes

The base validation command is:

```bash
python3 -m unittest discover -s tests
```

## Sprint 2 Definition of Done

Sprint 2 is complete when Genesis can reliably accept a founder idea, run the Research Department, persist the report and employee outputs, expose confidence and citations, track runtime behavior, support approval before later departments, and recover from interrupted research workflows.

Official marketplace APIs, richer dashboards, and downstream department automation can land after this foundation is stable.
