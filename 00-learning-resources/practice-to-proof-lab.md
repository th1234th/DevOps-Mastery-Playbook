# Practice-to-Proof Learning Lab

## Outcome

Turn one external learning resource into a small, reproducible work sample without copying course answers or exposing lab credentials. This is a repeatable learning workflow, not a replacement for the linked providers' own labs.

## Setup

Choose one resource from [the curated list](links.md) and a related in-repository exercise. Examples:

- Shell: Bandit or CMD Challenge plus the [Linux host incident lab](../01-linux-and-scripting/host-incident-lab/README.md).
- Containers: Docker documentation plus the [production image lab](../02-containerization/docker/production-image-lab/README.md).
- Kubernetes: official docs plus one [Kubernetes lab](../02-containerization/kubernetes/README.md).
- GitOps: Argo CD documentation plus the [Argo monitoring lab](../03-gitops-and-strategy/argocd-monitoring-lab/README.md).

Use only the external course's authorized sandbox and a disposable local environment. Do not publish passwords, flags, proprietary lesson content, personal data, or credentials.

## Tasks

1. Define an observable outcome that takes 60-120 minutes. Replace broad goals such as “learn Kubernetes” with a testable action.
2. Record a baseline: what you predict will happen, what is uncertain, and which command/output will verify the result.
3. Complete one external lesson or lab under its terms. Explain the key idea in your own words; do not copy a paid lesson or answer key.
4. Close the tutorial and reproduce a related task from a clean state using a repository practical. Capture the command, expected result, actual result, and one failure you diagnosed.
5. Check the safety boundary before running commands. Preserve only synthetic evidence, clean up temporary resources, and verify cleanup.
6. Write a five-minute handoff note: purpose, key decision, common failure, verification, and recovery.
7. Revisit the task one week later without notes. Record what you can still do and choose a focused next objective.

## Evidence Template

```text
Topic and resource:
Outcome:
Environment and version:
Safety boundary:
Baseline prediction:
Reproduction command/task:
Expected result:
Actual result:
Failure diagnosed:
Verification evidence:
Cleanup confirmation:
Five-minute explanation:
One-week recall result:
Next objective:
```

## Acceptance Criteria

- The outcome has an observable pass condition and a time bound.
- A related task is reproduced without following a solution line by line.
- Evidence distinguishes predictions from observations and includes verification and cleanup.
- No external course answers, secrets, or real personal/customer data are copied into the repository.
- The follow-up either demonstrates independent recall or narrows the next learning goal.

See the [example answer](practice-to-proof-answer.md) for a completed record.
