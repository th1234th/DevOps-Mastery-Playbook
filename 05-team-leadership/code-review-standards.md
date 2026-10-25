# Code Review Standards

## Review for

- Correctness, failure behavior, maintainability, and operational ownership.
- Least privilege, secret handling, data exposure, and dependency provenance.
- Resource requests and limits, scaling behavior, availability, and cost impact.
- Tests that exercise behavior and failure modes, not only implementation details.
- Observability, rollout safety, compatibility, rollback, and documentation.

## Team agreements

- Keep changes small enough to review; state intent, risk, test evidence, and rollout plan in the pull request.
- Use automated checks for repeatable policy. A reviewer should not be the only control for formatting, secret detection, or known unsafe defaults.
- Match review depth to risk. Production access, identity, data migration, and security-boundary changes deserve explicit owners.
- Give specific, respectful feedback and explain the risk behind requested changes.
- Do not equate line coverage with confidence. Agree on meaningful behavioral tests and document justified exceptions.
- Track decisions and follow-up work. Avoid making a pull request the permanent home for operational knowledge.

## Review prompt

Ask: “What could fail after this change, how will we know, who responds, and how do we safely recover?”