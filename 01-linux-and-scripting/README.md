# Linux and Scripting

## Practice objectives

- Navigate files and inspect ownership and permissions with `pwd`, `find`, `stat`, `id`, and `namei`.
- Inspect processes, memory, disk, logs, and services with `ps`, `free`, `df`, `journalctl`, and `systemctl`.
- Use pipes and exit codes intentionally. Prefer quoting variables and handling errors over clever one-liners.
- Use SSH keys, `known_hosts`, and `ssh-agent` safely; never disable host-key checking as a routine fix.
- Learn Git recovery in a disposable repository before attempting it on shared history.

## Bash safety checklist

- Use `set -Eeuo pipefail` for scripts where an unset variable or failed command should stop execution. Understand the exceptions before relying on it.
- Quote expansions such as `"$file"`; use arrays for argument lists.
- Validate inputs and check that destructive paths are non-empty and expected.
- Prefer explicit `--` before user-controlled path arguments when the command supports it.
- Make scripts idempotent where practical, and send diagnostics to stderr.
- Do not use `eval` on untrusted input or put credentials in command arguments.

## Mini-challenges

1. Write a script that reports filesystem usage above a configurable threshold and exits nonzero when breached.
2. Parse a service log into request count, error count, and p95 latency. State the log format assumptions.
3. Create a temporary directory and ensure cleanup happens on both success and failure.
4. Recover a mistaken commit in a throwaway Git repository using both `revert` and `reset`, then explain which is appropriate for shared history.

For a complete operational scenario that combines Linux host triage, structured-log analysis, tested scripts, incident evidence, and guarded cleanup, work through the [host incident response lab](host-incident-lab/README.md) and its [answer key](host-incident-lab/answer.md). It uses only synthetic logs copied to a temporary directory and does not modify host services.

For deliberate command-line puzzles, use the isolated [learning resources](../00-learning-resources/links.md).
