# DevOps Mastery Playbook

A practical, shareable path from foundational operations to leading reliable DevOps teams. The playbook combines the learning-resource URLs and challenge themes supplied with hands-on Kubernetes, GitOps, cloud, quality, and leadership exercises.

> The referenced images were not available as files in this workspace. Their described topics are represented here as written exercises; no image content has been invented.

## How to use this repository

Work through the phases in order, but treat them as a menu rather than a certification. Each lab should leave behind evidence: a short decision record, a tested configuration, a runbook, or a retrospective. Use a local cluster or a cloud sandbox that you own or are explicitly authorized to use. Never use real credentials in examples.

| Phase | Focus | Evidence to produce |
| --- | --- | --- |
| 0 | Learning resources and study habits | Weekly learning log and chosen labs |
| 1 | Linux, shell, Git, and containers | Reproducible scripts and container image |
| 2 | Kubernetes architecture and operations | Tested manifests, backup/restore notes, and failure drills |
| 3 | GitOps and delivery strategy | Promotion flow, rollback procedure, and drift report |
| 4 | Cloud and AI operations | Secure, observable deployment design |
| 5 | Reliability and leadership | SLO, on-call guide, and blameless review |

## Learning path

1. Start with the [curated resources](00-learning-resources/links.md). Choose one topic at a time and write down what you can now do without a tutorial.
2. Build foundations with [Linux and shell practice](01-linux-and-scripting/README.md) and [container labs](02-containerization/docker/README.md).
3. Study the [Kubernetes deep dives](02-containerization/kubernetes/README.md). Apply the manifests only in a disposable, authorized cluster.
4. Design a promotion and rollback flow using [GitOps and delivery strategy](03-gitops-and-strategy/README.md).
5. Practice cloud architecture and AI service operations with [cloud and AI labs](04-cloud-and-ai/README.md).
6. Make the work operable with [on-call and SRE guidance](05-team-leadership/sre-on-call-handbook.md) and [review standards](05-team-leadership/code-review-standards.md).

## Master challenges

- **Kubernetes security:** Prove a read-only developer identity can inspect Pods in one namespace but cannot mutate resources or discover protected production workloads. See [RBAC and namespace isolation](02-containerization/kubernetes/02-rbac-and-namespaces.md).
- **Workload health:** Demonstrate that an unhealthy process is restarted, while a dependency outage removes the Pod from service without causing a restart storm. See [probes](02-containerization/kubernetes/03-probes-healthchecks.md).
- **Capacity:** Explain what happens when Pod demand rises beyond current node capacity, and distinguish HPA, VPA, and cluster autoscaling. See [autoscaling](02-containerization/kubernetes/04-autoscaling.md).
- **Disconnected delivery:** Produce an inventory and verification procedure for images, charts, binaries, signatures, and dependencies before an offline deployment. See [air-gapped deployment](02-containerization/kubernetes/05-air-gapped-deployment.md).
- **Multi-cluster GitOps:** Diagnose a staging-success/production-failure scenario without making an unreviewed production change. See [multi-cluster troubleshooting](03-gitops-and-strategy/multi-cluster-gitops-troubleshooting.md).
- **Team leadership:** Define an SLO, an escalation path, and a blameless learning review for a realistic service incident.

## Quality bar

Every change should be reviewable, least-privileged, tested at the right level, observable, reversible, and documented for its operator. “It applied” is not the same as “it works.” Record assumptions, failure modes, ownership, and recovery steps.

The local-link checker can be run with Python 3:

```sh
python3 scripts/check_local_links.py
```

## Repository map

- [00-learning-resources](00-learning-resources/links.md)
- [01-linux-and-scripting](01-linux-and-scripting/README.md)
- [02-containerization](02-containerization/docker/README.md)
- [03-gitops-and-strategy](03-gitops-and-strategy/README.md)
- [04-cloud-and-ai](04-cloud-and-ai/README.md)
- [05-team-leadership](05-team-leadership/sre-on-call-handbook.md)

## Sharing

This repository is designed to work as a Git repository or an extracted ZIP. See [CONTRIBUTING](CONTRIBUTING.md) for the small maintenance and review checklist. External resources belong to their respective owners; check their terms before redistributing their content.