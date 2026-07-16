# Homelab Assistant

A conversational agent that monitors a small fleet of home machines and answers
natural-language questions about their state — CPU, memory, disk, GPU, running services
— with history and threshold-based alerts.

No model training involved: the project is about the engineering around an LLM —
structured data contracts, safety constraints, state management, and the gap between
what an LLM *says* it can do and what it does reliably.

## How it works

- **shim** — a stateless process on each machine. Serves current system state as one
  JSON `Snapshot`. No history, no LLM; runs unmodified everywhere.
- **orchestrator** (Mac Mini, not built yet) — polls every shim every 60 s into SQLite,
  evaluates alert rules, and answers NL queries via llama.cpp running on the GPU host.

```
 orchestrator (Mac Mini) ──poll 60s──> shim on each machine
        │  SQLite history, alert rules
        └──NL query──> llama.cpp (rivendell, RTX 5070 Ti)
```

## Machines

The fleet and per-machine details live in **[machines.md](machines.md)** (the canonical
registry). LAN addresses are kept out of the repo — see below.

## Repo map

| Path | What it is |
|---|---|
| [project-homelab-assistant.md](project-homelab-assistant.md) | Full spec — capabilities, schema, alert design, milestones |
| [machines.md](machines.md) | Canonical machine registry (hardware, roles, shim config) |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Current status and the next milestone's handoff |
| [CLAUDE.md](CLAUDE.md) | Working notes / conventions for this repo |
| [shim/](shim/) | The shim package — `schema.py`, `collectors.py`, `server.py` |

## Quick start (shim)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# GPU host (rivendell) only, for GPU metrics:
pip install pynvml

uvicorn shim.server:app --host 0.0.0.0 --port 8765 --log-level warning
curl -s http://localhost:8765/state | python3 -m json.tool
```

Bind shims to the LAN only — never expose port 8765 to the internet.

## A note on `.lan_addresses.md`

Private LAN addresses are deliberately **not** committed. They live in a gitignored
`.lan_addresses.md` (recreate it locally from the template if you clone fresh).
`machines.md` points there instead of listing addresses inline — this keeps network
topology out of the repo as basic hygiene in case it's ever shared or made public.

## Status

M1 complete — shim built and verified on the dev box (`ilum`). Next up (M2): deploy and
verify the shim on the GPU host. See [NEXT_STEPS.md](NEXT_STEPS.md).
