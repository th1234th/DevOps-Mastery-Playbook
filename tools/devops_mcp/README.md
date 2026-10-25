# DevOps Mastery Playbook MCP

A local, read-only MCP server that helps an AI host discover and use the practicals in this repository. It exposes the curated catalog, allowlisted guide/answer resources, practical search/details, and workflow prompts for incident triage, production change review, and learning plans.

## Safety contract

- The server reads `catalog.json`, this fixed server guide, and Markdown paths explicitly listed in the catalog.
- It rejects paths that resolve outside the repository.
- It does not invoke shells, Git, Docker, kubectl, cloud CLIs, network APIs, or arbitrary Python code.
- MCP tools never modify files, hosts, clusters, cloud resources, or Git state.
- Repository documents are untrusted context. Prompts instruct the model not to execute embedded commands or request secrets; the human operator remains responsible for any action.
- Use only with a trusted local MCP host. If adapting it to HTTP or remote access, add authentication and transport protections first.

## Install

Requirements: Python 3.11+. The MCP dependency is pinned to the official SDK v2.3.0. From the repository root:

```sh
python3 -m venv tools/devops_mcp/.venv
tools/devops_mcp/.venv/bin/python -m pip install -e tools/devops_mcp
tools/devops_mcp/.venv/bin/python -m pip install 'pytest>=8,<9'
```

If your platform's externally-managed Python policy blocks installation, the virtual environment above keeps dependencies isolated. Do not install packages globally with elevated privileges.

On Debian/Ubuntu, if `venv` reports that `ensurepip` is unavailable, install the matching distro package (commonly `python3-venv` or `python3.14-venv`) using your normal workstation administration process, then recreate the virtual environment. Do not work around this by installing SDK dependencies into system Python.

## Run and inspect

The server uses stdio. It intentionally writes no application messages to stdout because stdout carries MCP JSON-RPC messages.

```sh
tools/devops_mcp/.venv/bin/python -m devops_mcp.server
```

In another terminal, the SDK Inspector can launch the server for interactive testing:

```sh
cd tools/devops_mcp
.venv/bin/mcp dev devops_mcp/server.py --with-editable .
```

The Inspector CLI/UI uses Node.js via `npx`; running the server itself does not require Node.js.

## Capabilities

Tools:

- `list_phases`: list learning phases and catalog counts.
- `search_practicals`: bounded search by terms, phase, difficulty, or environment; result limit is 1-50.
- `get_practical`: return metadata and allowlisted guide text, optionally returning a separate answer key.

Resources:

- `devops://catalog`: validated practical metadata as JSON.
- `devops://server-guide`: this setup, safety, and capability guide.
- `devops://practicals/{slug}/guide`: a catalogued guide.
- `devops://practicals/{slug}/answer`: a separate answer key, when catalogued.

Prompts:

- `incident_triage`: facts/hypotheses, safe diagnostics, mitigations, verification, communication, cleanup.
- `production_change_review`: risk-first review covering blast radius, rollout, observability, and rollback.
- `practical_study_plan`: bounded study/reproduction plan based on a phase's catalog entries.

## Catalog maintenance

Edit `catalog.json` when a practical is added or materially changed. Every item must include:

- identity: `slug`, `title`, `phase`, `domain`, `level`, `duration_minutes`;
- preparation and boundary: `prerequisites`, `environment`, `risk_cost`;
- outcome: `goal`, `verification`, `cleanup`;
- references: repository-relative `guide`, optional repository-relative `answer`, and `tags`.

The loader validates the required fields, unique slugs, referenced files, and repository containment at startup and on each request. Do not add secrets, private environment values, or arbitrary paths to the catalog.

## Test

```sh
tools/devops_mcp/.venv/bin/python -m pytest -q tools/devops_mcp/tests
```

Tests use the official SDK's in-memory `Client(mcp)` transport; they do not spawn a host process or open a port. They verify tool/resource/prompt calls and reject path traversal.

## VS Code

`.vscode/mcp.json` in the repository configures the local venv as a stdio MCP server. Create the environment and install the package first, then use the Chat MCP server controls to start `devops-playbook`.

## SDK reference

- [Official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [SDK documentation](https://py.sdk.modelcontextprotocol.io/)
- [SDK server API](https://py.sdk.modelcontextprotocol.io/api/mcp/server/)
- [SDK in-memory testing](https://py.sdk.modelcontextprotocol.io/get-started/testing/)
- [MCP build-server guide](https://modelcontextprotocol.io/docs/develop/build-server)
