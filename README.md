# MAYA Agentic Harness
<img width="2172" height="724" alt="MAYA cyberpunk banner with CodesbyFebin" src="https://github.com/user-attachments/assets/ec520038-10d0-4ba4-968f-ea976a1aa059" />

![MAYA Agentic Harness](docs/maya-readme-banner.png)

**Local-first personal AI command center and agentic harness.**

MAYA is a complete visual command center and agent runtime built for operators who want systems that prove what happened. It combines a dark cyan multi-view dashboard with voice, tasks, memory, and workflows, paired with a Python harness that runs agent loops, enforces tool boundaries, stores memory, and writes full evidence traces of every execution. Everything is designed to run locally first so the operator remains in control.

## Ultimate Status

The current release delivers a working operator console and a local agent runtime. The dashboard supports voice input and spoken output, persistent chat history, live status, and multi-view navigation. The harness provides an agent loop that records every step, restricted tool wrappers for filesystem and terminal operations, a collection of workflow playbooks, a memory schema with a SQLite helper, and complete JSON evidence traces. The system is intentionally minimal so that every part can be inspected, modified, or extended without hidden dependencies.

## Why an Agentic Harness?

Most AI systems focus on the model and the prompt. An agentic harness is the full operational layer that turns a language model into a controllable system. It includes the interface the human uses, the tools the agent is allowed to call, the memory it can recall, the workflows it can follow, the approval gates that constrain action, and the evidence it leaves behind so the operator can verify exactly what occurred. Without a harness the model is only a text generator. With a harness it becomes an observable, auditable process.

MAYA treats the agent as a system that must be observable, controllable, and auditable. The dashboard is the operator console. The harness is the runtime that records every tool call, every decision, and every outcome. This design follows the principle that systems should prove what happened rather than merely claim that something was done. Evidence traces make the execution path inspectable after the fact. Tool wrappers enforce policy at the boundary. Memory is local and queryable. Workflows are declarative playbooks rather than opaque code. The result is an agent that can be trusted because its behavior can be verified.

## Core Features

The command center presents a multi-view dark interface with a live activity feed and a central AI core visual. Voice input uses the browser speech recognition API and spoken output uses the speech synthesis API, so the operator can work hands-free. Chat history and settings are stored locally in the browser. The agent runtime accepts text or voice queries, calls a model endpoint, and writes a complete JSON trace of the run. Workflow playbooks define ordered steps for common tasks such as research, code assistance, system monitoring, email triage, file organization, and news briefs. Tool wrappers restrict filesystem access to allowed roots and permit only a short allowlist of terminal commands. The memory store supports notes, facts, tasks, and traces with timestamps and provenance. Every agent run produces an evidence file that records the query, the steps taken, and the final result.

## Quick Start

Open the dashboard file in a modern browser that supports the Web Speech API. The file is self-contained and requires no build step. To run the local agent runtime, navigate to the harness directory, install the minimal dependencies, and start the stub server. The dashboard can then be pointed at the local endpoint through its settings panel. Once connected, voice or typed queries are sent to the runtime, responses are displayed and spoken, and evidence traces are written to disk for later inspection. The entire path from input to output is local and inspectable.

## Project Structure

The repository is organized so that the operator console and the runtime are clearly separated. The dashboard lives in its own directory as a single HTML file. The harness directory contains the agent loop, the local stub server, the workflow definitions, the tool wrappers, and the memory helpers. Documentation is kept in the wiki directory and a simple landing page is provided under docs. Branding assets, including the hero banner and favicon, are also under docs and public. This layout keeps the surface area small while still supporting extension.

## Architecture

The system has two layers. The dashboard layer runs in the browser. It captures voice or typed input, renders the multi-panel interface, stores local state, and sends requests to the agent runtime. The harness layer runs in Python. It receives requests, executes the agent loop, calls tools under policy constraints, writes evidence traces, and stores memory. Data flows from the operator through the dashboard into the runtime and back, with every step recorded. The architecture is intentionally simple so that any part can be replaced or extended without breaking the evidence contract.

## Workflows

Playbooks are declarative YAML files that describe a named task, the agent style to use, the tools required, and the ordered steps to follow. Examples include a morning digest that gathers calendar, inbox, and news items; a deep research playbook that gathers sources and produces a cited brief; a code assistant that plans, implements, and verifies changes; a system monitor that checks local health; an email triage that classifies and drafts replies; a file organizer that scans and proposes moves; and a news brief that synthesizes current items on a topic. Each playbook is designed so that the steps can be inspected and the tools they require can be constrained.

## Tools

Tool wrappers enforce safety boundaries at the point of execution. The filesystem wrapper restricts list, read, and write operations to a set of allowed roots and refuses paths that fall outside them. The terminal wrapper permits only a short allowlist of safe commands and rejects everything else. Both wrappers return structured results that can be recorded in evidence traces. Additional tools can be added by following the same pattern of allowlists and structured returns. The goal is that no tool can perform an action that has not been explicitly permitted.

## Memory and Evidence

Memory entries follow a simple schema that includes an identifier, a type, content, a source, a timestamp, optional tags, and an evidence field. Types include notes, facts, tasks, traces, and workflow runs. The SQLite helper creates a single-file database that can be queried or exported. Evidence traces are written as JSON files that record the original query, the sequence of steps taken, the status of each step, and the final result. These traces make it possible to reconstruct exactly what the agent did, which tools it called, and what it returned. The combination of structured memory and complete traces is the practical expression of the project tagline: systems that prove what happened.

## Branding

The visual identity uses a near-black background, phosphor green accents, and cyan highlights. The geometric mark is a simple circle with radial lines that suggests a core or a sensor. The hero banner and favicon follow the same palette and geometry. The tagline appears consistently across the dashboard, the documentation, and the landing page. All branding assets are included in the repository so that the project can be forked or extended while retaining a coherent appearance.

## Roadmap

Future work includes richer tool wrappers, additional workflow playbooks, a more complete memory index, evidence hashing for stronger provenance, and packaging options for desktop use. The current design already supports these extensions because the evidence contract and the tool boundary are explicit. Operators can add new playbooks by writing YAML, add new tools by following the wrapper pattern, and inspect every run through the traces that are already produced.

## Live runtime events

The command centre connects to the local backend at /v1/events using the maya.events.v1 envelope. It receives a hello frame with backend health and configured tool metadata, then run_started, tool_event, policy_denied, and run_result frames while requests run. Events carry a sequence number, UTC timestamp, and run ID. The client may send ping frames; the server does not accept agent-starting commands over this channel. The earlier /ws endpoint remains available for clients using the unversioned event shape.

The stream is backed by Maya's current agent loop. Tool events expose only the tool name, status, and round. Prompts, arguments, file contents, and model responses stay out of the broadcast stream. Per-client queues are bounded, the service sends heartbeats, and the dashboard reconnects with backoff while retaining the HTTP health check as a fallback. Trace frames report whether a local execution log was written; this backend labels those logs unverified.

WebSocket browser origins use the MAYA_ALLOWED_ORIGINS allowlist. Its default permits the local dashboard on ports 5500. For a Pages preview, explicitly add the exact deployed origin to the backend environment only when you trust that origin; the public showcase does not connect to a backend by default.

## License

Apache-2.0

Built by CodesbyFebin · systems that prove what happened.

---

This documentation is written to describe the MAYA Agentic Harness in full. It covers the purpose of an agentic harness, the features of the current release, the quick start path, the project structure, the architecture, the workflows, the tools, the memory and evidence system, the branding, and the roadmap. The goal is that an operator can understand the system, run it locally, inspect its behavior, and extend it while remaining confident that every action can be verified after the fact.


## GitHub Pages

MAYA's public static showcase is published at <https://codesbyfebin.github.io/Maya-Agentic-Harness/>. The hosted console starts disconnected and does not probe visitors' localhost. A backend URL must be configured explicitly, and the backend must allow the Pages origin in its CORS policy. The local dashboard served from `127.0.0.1:5500` remains the intended operator console.


