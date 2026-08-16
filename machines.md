# Machines

**Canonical registry of the machines in the Homelab Assistant project.** This is the
single source of truth for per-machine facts - hostnames, hardware, roles, shim config,
and gotchas. Other docs (`CLAUDE.md`, `project-homelab-assistant.md`, `NEXT_STEPS.md`)
should summarize and link here rather than restate these details.

> Each shim reports a `hostname` field; alert rules and the orchestrator key off it, so
> the **canonical hostname** below must match what that machine's shim actually returns.

---

## rivendell - primary compute / LLM host

| | |
|---|---|
| **Canonical hostname** | `rivendell` |
| **Role** | Primary compute; runs llama.cpp (the LLM layer for the whole system) |
| **OS / platform** | Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-124-generic x86_64)  |
| **CPU** | Intel(R) Core(TM) Ultra 7 265KF / 20 processors |
| **RAM** | 32 GB |
| **GPU** | NVIDIA GeForce RTX 5070 Ti, 16 GB |
| **Disks** |CT2000P510SSD8 - 2 TB: NVMe layout |
| **LAN address** | Check in local [lan_addresses.py](orchestrator/lan_addresses.py) file |
| **Shim port** | 8765 |
| **Polling interval** | 60 sec default (spec notes a shorter interval may be warranted when training jobs run) |
| **Runs / services** | llama.cpp - models: `LFM2.5-2.6B` (main), `Qwen3.5-9B` (log/code reasoning) |
| **GPU / llama.cpp** | `pynvml` installed here **only** - lights up the `gpu` field |
| **Shim status** | Deployed as **systemd service**, restarts automatically; `gpu`/`llama.cpp` confirmed populated |

---

## caladan - Secondary compute / web application VM.  might add network monitoring processes in the future to this VM

| | |
|---|---|
| **Canonical hostname** | `caladan` |
| **Role** | Secondary compute; runs web applications |
| **OS / platform** |  Ubuntu 20.04.6 LTS (GNU/Linux 5.15.0-181-generic x86_64) |
| **CPU** | AMD A8-3800 APU with Radeon(tm) HD Graphics / 4 processors |
| **RAM** | 16 GB |
| **GPU** | Sumo [Radeon HD 6550D] |
| **Disks** | CT480BX200SSD1 - 500 GB: ATA layout |
| **LAN address** | Check in local [lan_addresses.py](orchestrator/lan_addresses.py) file |
| **Shim port** |  8765 |
| **Polling interval** | 60 sec |
| **Runs / services** | Santa picker server - maybe add a service check so assistant can report on its status |
| **GPU / llama.cpp** | AMD integrated GPU - **not** covered by `pynvml` (If GPU stats are ever wanted, they'd come from `radeontop`/sysfs, not pynvml - but this is an old TeraScale card, so low priority.) |
| **Shim status** | Deployed as **systemd service**, restarts automatically |

---

## mac-mini - orchestrator

| | |
|---|---|
| **Canonical hostname** | `ChibaCity` |
| **Role** | Orchestration node - polling daemon, SQLite history store, alert engine, query handler |
| **OS / platform** | macOS (Mac Mini M2) |
| **CPU** | Apple M2 / 8 processors |
| **RAM** | 8 GB |
| **Disks** |  APPLE SSD AP0256Z, 500 MB: NVMe layout |
| **LAN address** | Check in local [lan_addresses.py](orchestrator/lan_addresses.py) file |
| **Shim port** | 8765 |
| **Polling interval** | 60 sec (polls itself + the others) |
| **Runs** | Orchestrator daemon + its own shim (both need **manual activation**) |
| **GPU / services** | none - `gpu` and `services.llamacpp` report `null` |
| **Shim status** | deployed; needs **manual activation** (not a service yet - launchd blocked on sudo) |

---

## ilum - Windows dev box (where Claude Code runs)

| | |
|---|---|
| **Canonical hostname** | `ilum`  |
| **Role** | Development workstation; shim is developed and first-tested here |
| **OS / platform** | Windows 11 host; Claude Code + shim run under **WSL2 Ubuntu** |
| **CPU** | Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz / 8 processors |
| **RAM** | 64 GB |
| **GPU** | Radeon RX 570 Series (8 GB) - **not collected by pynvml** |
| **Disks** | Samsung  SSD 980 PRO - 1 TB: NVMe layout |
| **LAN address** | Check in local [lan_addresses.py](orchestrator/lan_addresses.py) file |
| **Shim port** | 8765 |
| **Polling interval** | 60 sec |
| **GPU / services** | none - `gpu` and `services.llamacpp` report `null` |
| **Shim status** | Not set up - box is not SSH-accessible right now |
