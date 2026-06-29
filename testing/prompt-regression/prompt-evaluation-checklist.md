# Prompt Evaluation Checklist

Every Genesis prompt must be evaluated before production use.

## Required Checks

- [ ] Employee ID is present
- [ ] Department is present
- [ ] Mission is clear
- [ ] Authority boundary is defined
- [ ] Inputs are structured
- [ ] Output schema is documented
- [ ] Business rules are included
- [ ] Quality checklist is included
- [ ] Hallucination behavior is defined
- [ ] Low-confidence behavior is defined
- [ ] Prompt version is present

## Test Cases

Each prompt should pass:

- Normal input
- Missing input
- Invalid input
- Ambiguous input
- Low-confidence case
- Unsupported request

## Approval

A prompt is production-ready only after it passes evaluation and is committed with a version number.
