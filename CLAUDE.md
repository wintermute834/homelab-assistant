# CLAUDE.md

Homelab Assistant — a conversational agent that monitors three machines and answers
natural-language questions about their state. Full spec: `project-homelab-assistant.md`.
Current status / handoff: `NEXT_STEPS.md` (source of truth for "what's next").

## Architecture

- **shim** (`shim/`) — stateless process on *each* machine. Serves current system state
  as one JSON `Snapshot`. No history, no LLM. Runs unmodified everywhere.
- **orchestrator** (Mac Mini, not built yet) — polls shims every 60s into SQLite, runs
  alert rules, answers NL queries via Ollama on rivendell.

Machines: **rivendell** (Linux, RTX 5070 Ti, runs Ollama) · **Mac Mini M2** (orchestrator)
· **ilum** (this WSL2 dev box, where Claude Code runs).

## Run & test the shim

```bash
.venv/bin/uvicorn shim.server:app --host 0.0.0.0 --port 8765 --log-level warning
curl -s http://localhost:8765/state | python3 -m json.tool   # full snapshot
curl -s http://localhost:8765/health                          # liveness
```

Local env is `.venv/` in the project root. Bind to LAN only — never expose to the internet.

## Conventions & gotchas

- **`schema.py` is the contract.** The `Snapshot` Pydantic models are enforced, not just
  documentation — changes to the payload shape go there first.
- **Collectors degrade to `null`, never throw.** Absent hardware/services (`gpu`,
  `services.ollama`) must return `null`, so the shim runs on any machine unchanged.
- **`pynvml` is rivendell-only.** It's commented out in `requirements.txt`; the GPU
  collector falls back to `null` when it (or an NVIDIA driver) is missing.
- **Disk collector filters pseudo-filesystems** (squashfs, overlay, tmpfs, 9p, `/mnt/wsl`,
  `/snap`, `/var/lib/docker`, duplicate devices). Keep this — otherwise WSL bind-mounts
  show bogus 100%-full volumes and false-fire the disk alert.
