# Contributing to Genesis AI

Genesis AI is built as an engineering-first AI platform. Every contribution must preserve clarity, modularity, and traceability.

## Engineering Principles

1. Constitution first.
2. Documentation before implementation.
3. Small, reviewable commits.
4. Every feature requires tests where applicable.
5. Architecture changes require an ADR.
6. No undocumented AI behavior.
7. No hardcoded secrets.

## Branch Strategy

- `main` contains stable work.
- `feature/*` contains planned feature work.
- `docs/*` contains documentation or specification changes.
- `fix/*` contains corrections.
- `hotfix/*` contains urgent production fixes.

## Commit Convention

Use conventional commits:

```text
type(scope): summary
```

Examples:

```text
feat(research): add trend report schema
docs(handbook): update sprint 1d backlog
fix(database): add missing index
chore(ci): add validation workflow
```

## Pull Request Checklist

Before opening a PR:

- [ ] Requirement exists or task is listed in `implementation/backlog.md`
- [ ] Documentation updated
- [ ] Tests or validation updated where applicable
- [ ] No secrets committed
- [ ] File names follow repository conventions
- [ ] Architecture impact considered

## AI Prompt Contribution Rules

Every production prompt must include:

- Employee ID
- Department
- Mission
- Authority
- Inputs
- Output schema
- Quality checklist
- Version

Prompts are treated as production assets, not casual text.
