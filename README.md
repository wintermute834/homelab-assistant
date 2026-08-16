# Homelab Assistant

A conversational agent that monitors a small fleet of home machines and answers natural-language questions about their state
CPU, memory, disk, GPU, running services, and (planned) threshold-based alerts.

No model training involved: the project is about the engineering around an LLM -
structured data contracts, safety constraints, state management, and the gap between
what an LLM *says* it can do and what it does reliably.

## How it works

- **shim** - A stateless process on each machine.
  - Serves current system state as one JSON Snapshot conforming to schema.py.
  - Lives in its own repo and is checked out as a git submodule at `shim/` and runs unmodified everywhere.
- **orchestrator** - a daemon that polls every shim every 60 sec, stores
  each snapshot in SQLite, and answers NL queries via llama.cpp running on the GPU
  host (rivendell). The LLM fetches state with **tools** - latest snapshots per
  machine, historical snapshots by hostname/time range, current UTC time - instead of
  having state injected into the prompt. The live system prompt, model choice
  (`LFM2.5-2.6B`), and tool wiring all live in `orchestrator/orchestrator.py`.

## Machines

The fleet and per-machine details live in **[machines.md](machines.md)** (the canonical
registry). LAN addresses are kept out of the repo - see below.

## Repo map

| Path | What it is |
|---|---|
| [project-homelab-assistant.md](project-homelab-assistant.md) | Full spec - capabilities, schema, alert design, milestones |
| [machines.md](machines.md) | Canonical machine registry (hardware, roles) |
| [NEXT_STEPS.md](NEXT_STEPS.md) | Current status and the next milestone's handoff |
| [CLAUDE.md](CLAUDE.md) | LLM working notes / conventions for this repo |
| [shim/](shim/) | Git submodule - shim package (`schema.py`, `collectors.py`, `server.py`), own requirements |
| [orchestrator/](orchestrator/) | Polling daemon, SQLite history, llama.cpp harness + tools, CLI |

## Quick start

Use `uv` for easy Python version and package management

### Shim (on each monitored machine)

```bash
# Clone repo
git clone git@github.com:wintermute834/homelab-shim.git
cd homelab-shim

# Set up virtual environment
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
# rivendell only, for GPU metrics:
uv pip install pynvml

# Run shim server and test
uvicorn server:app --host 0.0.0.0 --port 8765
curl -s http://localhost:8765/state | python3 -m json.tool
```

Bind shims to the LAN only - never expose port 8765 to the internet.

### Orchestrator

```bash
# Clone repo
git clone git@github.com:wintermute834/homelab-assistant.git
cd homelab-assistant

# Set up virtual environment
uv venv
source .venv/bin/activate
uv pip install -r orchestrator/requirements.txt

# Get lan addresses
mv _lan_addresses_template.py lan_addresses.py # then, fill in the real LAN IPs

# Run orchestrator polling loop and chat CLI
python -m orchestrator
```

Needs the `shim/` submodule checked out (`git submodule update --init`).
`snapshots.db` is created on first run and collection runs in the background while the CLI handles the conversation.

## A note on `.lan_addresses.md`

Private LAN addresses are deliberately **not** committed, they live in a gitignored `lan_addresses.py`.

Rename or copy `_lan_addresses_template.py` to `lan_addresses.py` and fill in the real IPs.

`machines.md` points there instead of listing addresses inline.

## Status

See [NEXT_STEPS.md](NEXT_STEPS.md) for what has been completed and what is to come.
