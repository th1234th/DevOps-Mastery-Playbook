# Contributing

Keep this playbook useful to an engineer who is operating a real service, not just preparing for an interview.

## Before submitting a change

- Prefer a small, testable example and state its assumptions and prerequisites.
- Use placeholders for accounts, hostnames, and credentials. Never commit secrets, private keys, recovery codes, or production data.
- Keep Kubernetes examples least-privileged and label destructive or cost-incurring actions clearly.
- Add a rollback or cleanup step to every lab that creates resources.
- Check local Markdown references with `python3 scripts/check_local_links.py`.
- Have an operator or peer review changes that affect security, availability, or incident response.

## Lab safety

Use systems you own or have explicit permission to administer. Keep security exercises in intentionally vulnerable training environments. Do not run load tests, scans, or failure drills against third-party systems.