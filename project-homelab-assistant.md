# Project 2 - Homelab Assistant

## Goal

Build a conversational agent that knows the home infrastructure - rivendell, the Mac Mini,
and the Windows dev box - and can answer natural language questions about system state,
running services, and resource usage. Optionally execute a small set of pre-approved safe
commands on request.

This is a practical deployment project. The learning comes not from training a model but
from the work of integrating one into a real system: tool design, structured data contracts,
safety constraints, state management, and the gap between what an LLM *says* it can do
and what it can actually do reliably.

By the end, there should be something genuinely useful that gets used after the summer.

---

## Core Capabilities (Scoped - Do Not Expand Until These Are Solid)

### 1. Query
Ask the assistant questions about the current state of the infrastructure.

Examples:
- "Is rivendell's GPU being used right now?"
- "Which llama.cpp models are currently loaded?"
- "What's the disk usage on the NVMe?"
- "Is the Mac Mini reachable?"
- "What processes are using the most memory on rivendell?"

### 2. History
Ask about recent state over time, not just right now.

Examples:
- "Was rivendell under heavy load last night?"
- "When did the llama.cpp service last restart?"
- "Has disk usage been climbing this week?"

### 3. Alert
The system proactively notifies when something crosses a defined threshold -
without being asked.

Examples:
- GPU temperature exceeds threshold
- Disk usage crosses 80%
- A monitored service stops responding
- RAM usage stays above threshold for more than N minutes

---

## Architecture

```
    ┌───────────────────────────────────────────────┐
    │                  Mac Mini M2                  │
    │                                               │
    │  ┌─────────────────────────────────────────┐  │
    │  │         Orchestration Daemon            │  │
    │  │  - Polls shims on a schedule            │  │
    │  │  - Writes to history store (SQLite)     │  │
    │  │  - Handles user queries via CLI/web     │  │
    │  │  - Routes queries to LLM on rivendell   │  │
    │  │  - Triggers alerts when rules fire      │  │
    │  └─────────────────────────────────────────┘  │
    └──────────────────────┬────────────────────────┘
                           │ LAN (SSH or HTTP)
       ┌───────────┬───────┴─────┬──────────────┐
       │           │             │              │
┌──────▼────┐ ┌────▼─────┐ ┌─────▼──────┐ ┌─────▼────────┐
│ rivendell │ │ Mac Mini │ │ Windows PC │ │   caladan    │
│           │ │          │ │            │ │              │
│  shim +   │ │   shim   │ │   shim     │ │   shim +     │
│ llama LLM │ │  (self)  │ │            │ │ santa picker │
└───────────┘ └──────────┘ └────────────┘ └──────────────┘
```

### Components

**Shim** (runs on each monitored machine)
A lightweight Python process (or script called on demand) that collects system state
and returns it as a structured JSON payload. The shim exposes a minimal local HTTP
API - one endpoint, one response. It does not talk to the LLM. It only collects data.

**Orchestration Daemon** (runs on Mac Mini)
The brain of the system. Polls each shim on a schedule, writes results to the history
store, listens for user input, constructs prompts from current and historical state,
calls the LLM on rivendell, and sends alerts when rules fire.

**LLM Layer** (rivendell / llama.cpp)
`LFM2.5-2.6B` handles the majority of conversational queries - it's fast and cheap for
simple factual questions about structured data. `Qwen3.5-9B` can be invoked for
queries that require interpreting logs or reasoning about code-level issues.
No frontier model needed for this project.

**History Store** (SQLite on Mac Mini)
A simple append-only table of timestamped JSON snapshots from each machine.
SQLite is sufficient - this is not a high-volume database. The orchestrator queries it
to provide historical context to the LLM.

**User Interface**
Start with a CLI. A simple web interface is a stretch goal.

---

## Shim - Data Schema

Each shim returns a JSON object conforming to this schema.
All machines return the same top-level structure; fields that don't apply are null.

```json
{
  "hostname": "rivendell",
  "timestamp": "2026-07-17 06:29:32",
  "cpu": {
    "percent": 0.2,
    "core_count": 20,
    "load_avg_1m": 0.06
  },
  "memory": {
    "total_gb": 31.1,
    "used_gb": 3.4,
    "percent": 10.9
  },
  "disk": [
    {
      "mount": "/",
      "total_gb": 1688.0,
      "used_gb": 146.5,
      "percent": 8.7
    }
  ],
  "gpu": {
    "name": "NVIDIA GeForce RTX 5070 Ti",
    "memory_total_mb": 16303,
    "memory_used_mb": 14521,
    "utilization_percent": 0,
    "temperature_c": 42
  },
  "network": {
    "interfaces": [
      "ethernet0"
    ],
    "reachable": true
  },
  "services": {
    "llama_cpp": {
      "running": true,
      "models": [
        {
          "name": "LFM2.5-2.6B",
          "status": "loaded",
          "modalities": [
            "text"
          ]
        },
        {
          "name": "Qwen3.5-9b",
          "status": "sleeping",
          "has_vision": [
            "text",
            "vision"
          ]
        },
        ...
      ]
    }
  },
  "uptime_hours": 42.3
}
```

Fields not applicable to a machine (e.g., `gpu` on the Mac Mini or Windows box)
should be returned as `null`, not omitted, so the schema stays consistent.

---

## Shim Implementation Notes

**Library:** `psutil` for CPU/memory/disk. `pynvml` or `nvidia-smi` subprocess call for GPU
(rivendell only). llama.cpp running status via `localhost:8080/models`

**Transport:** Simple HTTP server (FastAPI) listening on a LAN port.
Not exposed to the internet. Local network only.

**Polling:** The Mac Mini orchestrator polls each shim every 60 seconds by default.
Configurable per-machine. Rivendell may warrant a shorter interval when training jobs are running.

**Windows shim note:** `psutil` works on Windows. GPU on the Windows box is an older card -
collect what NVML exposes but don't rely on it. CPU/memory/disk are the useful metrics there.

---

## Orchestration Daemon - Key Responsibilities

### Polling Loop
```
every 60 seconds:
  for each registered machine:
    fetch shim JSON
    write snapshot to SQLite (machine, timestamp, json_blob)
    evaluate alert rules against current snapshot
    if rule fires and cooldown has elapsed: send alert
```

### Query Handling
When the user asks a question:
1. Fetch the latest snapshot for each machine from SQLite
2. Fetch relevant history (e.g., last 24 hours of snapshots) if the query is time-based
3. Construct a prompt: system context describing the infrastructure + current state JSON
   + historical summary if relevant + user question
4. Send to llama.cpp on rivendell (`Qwen3.5-4B` by default)
5. Return response to user

**System prompt template (starting point):**
```
You are a homelab infrastructure assistant. You have access to real-time and historical
data from four machines:
  rivendell (Linux, primary compute, RTX 5070 Ti GPU),
  ChibaCity (macOS, orchestration node),
  ilum (Windows 11, dev workstation),
  caladan (Linux, Santa Picker web host)

Current state data is provided as JSON. Answer questions factually based on this data.
If the data does not contain enough information to answer, say so - do not guess.
Keep responses concise.

Current snapshot:
{current_state_json}
```

### Alert Rules
Defined as a simple config file (YAML or JSON). Example:

```yaml
alerts:
  - name: rivendell_gpu_temp_high
    machine: rivendell
    field: gpu.temperature_c
    condition: ">"
    threshold: 85
    cooldown_minutes: 30
    message: "rivendell GPU temperature is {value}°C"

  - name: rivendell_disk_warning
    machine: rivendell
    field: disk[0].percent
    condition: ">"
    threshold: 80
    cooldown_minutes: 120
    message: "rivendell root disk at {value}% capacity"

  - name: llama_cpp_service_down
    machine: rivendell
    field: services.llama_cpp.running
    condition: "=="
    threshold: false
    cooldown_minutes: 10
    message: "llama.cpp server is not running on rivendell"
```

---

## Safety Constraints

If we add the ability for the assistant to *execute* commands (stretch goal, not MVP),
this section governs what is and is not permitted.

### Permitted (read-only, pre-approved)
- Return current system stats (already handled by shim - no extra risk)
- Run `curl 192.168.0.0:8080/models`
- Show recent log tail (specified log files only, not arbitrary paths)
- Check if a service is running (`systemctl is-active <service>`)

### Requires Explicit Confirmation
- Restarting a specific pre-approved service
- Pulling a new llama.cpp model

### Never Permitted (hard-coded off, not configurable)
- Arbitrary shell command execution
- File deletion or modification
- Network configuration changes
- Any command with `sudo` that isn't in the pre-approved list
- Anything affecting the host OS package manager

**Design principle:** The LLM decides *what* to do. A separate, dumb, rule-based layer
decides *whether it is allowed*. The LLM should never be in the path of permission decisions.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11+ | All components |
| `psutil` | CPU, memory, disk metrics (all machines) |
| `pynvml` | GPU metrics (rivendell only) |
| `FastAPI` | Shim HTTP server |
| `httpx` | Orchestrator polling shims and llama.cpp |
| `SQLite` (via `sqlite3`) | History store on Mac Mini |
| `llama-server` | LLM inference on rivendell |
| `schedule` | Polling loop on orchestrator |
| `click` or `argparse` | CLI interface |
| YAML config | Alert rules, machine registry |

No heavy frameworks. Keep dependencies minimal and explicit.

---

## Division of Labor

| Task | Lead |
|---|---|
| Shim implementation (all machines) | Son (Python) |
| Mac Mini orchestration daemon - polling loop | Dad (infra) + Son (Python) |
| SQLite history store schema and queries | Son |
| LLM prompt engineering and query handler | Son (with iteration) |
| Alert rule engine | Shared |
| System prompt design and testing | Shared |
| Network / firewall / service setup | Dad |
| CLI interface | Son |
| Documentation | Shared |

---

## Milestones

| Milestone | Description | Target week |
|---|---|---|
| M1 | Shim running on rivendell, returning valid JSON | Week 2 |
| M2 | Shims running on all three machines | Week 3 |
| M3 | Mac Mini orchestrator polling all shims; writing to SQLite | Week 4 |
| M4 | First LLM query working end-to-end (ask a question, get an answer) | Week 5–6 |
| M5 | Alert rules defined and firing correctly | Week 7 |
| M6 | History-aware queries working ("what was load like last night?") | Week 8 |
| M7 | CLI polished; system runs stably for a week unattended | Week 9–10 |

---

## Stretch Goals (only after M7 is complete)

- Simple web UI (Flask template or minimal React) replacing the CLI
- Safe command execution with the confirmation layer described above
- Natural language alert configuration ("tell me if the GPU gets too hot")
- Weekly summary report generated by the LLM and delivered via local notification
- Slack or ntfy.sh notification integration for alerts instead of just CLI output

---

## Notes & Decisions

*Log decisions here as the project evolves.*

- **LLM for queries:** `LFM2.5-2.6B` (fast, sufficient for structured-data QA)
- **LLMs for log analysis / complex queries:** `Qwen3.5-9B`, `Qwen3.6-27b`
- **Polling interval:** 60 seconds (adjustable per machine in config)
- **History retention:** 30 days (older rows pruned by a nightly cleanup job)
- **Shim port:** TBD (choose something above 8000, document in config)
- **Interface:** CLI first; web UI is stretch
- **Alert delivery:** Local notification / log file first; ntfy.sh integration is stretch
- **Shim port:** 8765 (chosen, was TBD)
- **Shim transport:** FastAPI + uvicorn; endpoints `GET /state` and `GET /health`
- **Schema enforcement:** shim payload modeled as Pydantic in `shim/schema.py` - the
  JSON contract is validated, not just documented
- **llama.cpp reporting:** shim reports both `models_available` (installed, via `/api/tags`)
  and `models_loaded` (in memory, via `/api/ps`); `/api/tags` is the liveness signal so
  `running` is reliable even when no model is loaded
- **Disk collection:** pseudo/virtual filesystems and duplicate devices filtered out
  (squashfs/overlay/tmpfs/9p, `/mnt/wsl`, `/snap`, `/var/lib/docker`) so `disk[0]` is
  always a real volume
- **M1 done (2026-06-24):** shim verified returning valid JSON on the WSL2 dev box
  (`ilum`); gpu/llama.cpp degrade to null where absent. Next: deploy + test on rivendell
  (see `NEXT_STEPS.md`)
