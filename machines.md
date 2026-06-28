# Machines

**Canonical registry of the machines in the Homelab Assistant project.** This is the
single source of truth for per-machine facts — hostnames, hardware, roles, shim config,
and gotchas. Other docs (`CLAUDE.md`, `project-homelab-assistant.md`, `NEXT_STEPS.md`)
should summarize and link here rather than restate these details.

> Each shim reports a `hostname` field; alert rules and the orchestrator key off it, so
> the **canonical hostname** below must match what that machine's shim actually returns.

Fields marked `_TODO_` are unconfirmed — fill in as you verify on the real machine.

---

## rivendell — primary compute / LLM host

| | |
|---|---|
| **Canonical hostname** | `rivendell` |
| **Role** | Primary compute; runs Ollama (the LLM layer for the whole system) |
| **OS / platform** | Ubuntu 24.04.4 LTS (GNU/Linux 6.8.0-124-generic x86_64)  |
| **CPU** | Intel(R) Core(TM) Ultra 7 265KF / 20 processors |
| **RAM** | 32 GB |
| **GPU** | NVIDIA GeForce RTX 5070 Ti, 16 GB |
| **Disks** |CT2000P510SSD8 - 2 TB: NVMe layout |
| **LAN address** | Check in local .lan_addresses.md file |
| **Shim port** | 8765 |
| **Polling interval** | 60 s default (spec notes a shorter interval may be warranted when training jobs run) |
| **Runs / services** | Ollama — models: `qwen2.5:3b` (default), `qwen2.5-coder:14b` (log/code reasoning) |
| **GPU metrics** | `pynvml` installed here **only** — lights up the `gpu` field |
| **Shim deploy** | **Manual, by the user** — do not ssh/scp on their behalf. Steps in `NEXT_STEPS.md`. |
| **Shim status** | M2 pending — deploy + verify `gpu`/`ollama` populated |
| **Notes** | Primary machine; hands-on control preferred. |

---

## caladan — Secondary compute / web application VM.  might add network monitoring processes in the future to this VM

| | |
|---|---|
| **Canonical hostname** | `caladan` |
| **Role** | Secondary compute; runs web applications |
| **OS / platform** |  Ubuntu 20.04.6 LTS (GNU/Linux 5.15.0-181-generic x86_64) |
| **CPU** | AMD A8-3800 APU with Radeon(tm) HD Graphics / 4 processors |
| **RAM** | 16 GB |
| **GPU** | Sumo [Radeon HD 6550D],  _TODO_ GB |
| **Disks** | CT480BX200SSD1 - 500 GB: ATA layout |
| **LAN address** | Check in local .lan_addresses.md file |
| **Shim port** |  8765 |
| **Polling interval** | 60 s default (spec notes a shorter interval may be warranted when training jobs run) |
| **Runs / services** |  _TODO_ |
| **GPU metrics** | AMD integrated GPU — **not** covered by NVML/`pynvml` (NVIDIA-only), so the shim's `gpu` field degrades to `null`. CPU/mem/disk are the useful metrics here. (If GPU stats are ever wanted, they'd come from `radeontop`/sysfs, not pynvml — but this is an old TeraScale card, so low priority.) |
| **Shim deploy** | **Manual, by the user** — do not ssh/scp on their behalf. Steps in `NEXT_STEPS.md`. |
| **Shim status** | Not yet deployed |
| **Notes** | Secondary machine;  |

---

## mac-mini — orchestrator

| | |
|---|---|
| **Canonical hostname** | `ChibaCity` |
| **Role** | Orchestration node — polling daemon, SQLite history store, alert engine, query handler |
| **OS / platform** | macOS (Mac Mini M2) |
| **CPU** | Apple M2 |
| **RAM** | 8 GB |
| **Disks** |  APPLE SSD AP0256Z, 500 MB: NVMe layout |
| **LAN address** | Check in local .lan_addresses.md file |
| **Shim port** | 8765 |
| **Polling interval** | 60 s (polls itself + the others) |
| **Runs / services** | Orchestrator daemon (not built yet) + its own shim |
| **GPU / Ollama** | none — `gpu` and `services.ollama` report `null` |
| **Shim status** | Not yet deployed |
| **Notes** | The "brain"; everything else reports to it. |

---

## ilum — Windows dev box (where Claude Code runs)

| | |
|---|---|
| **Canonical hostname** | `ilum`  |
| **Role** | Development workstation; shim is developed and first-tested here |
| **OS / platform** | Windows 11 host; Claude Code + shim run under **WSL2 Ubuntu** |
| **CPU** | Intel(R) Core(TM) i7-9700K CPU @ 3.60GHz / 8 processors |
| **RAM** | 64 GB |
| **GPU** | Radeon RX 570 Series (8 GB) - collect what NVML exposes but don't rely on it; CPU/mem/disk are the useful metrics |
| **Disks** | Samsung  SSD 980 PRO - 1 TB: NVMe layout |
| **LAN address** | Check in local .lan_addresses.md file |
| **Shim port** | 8765 |
| **Polling interval** | 60 s |
| **Runs / services** | none monitored — `gpu` and `services.ollama` report `null` |
| **Shim status** | M1 verified here — `/state` returns schema-valid JSON |
| **Gotchas** | Stock Python 3.12 had no pip/venv (needed `sudo apt install python3-venv python3-pip`). WSL pollutes `psutil.disk_partitions` with bind-mounts/overlays (some bogusly 100% full) — handled by the disk filter in the shim. |

---

## Open questions to reconcile

- **Hostname naming.** Spec's system prompt (lines 198-199) uses `mac-mini` and
  `windows-dev`; usage/memory calls the dev box `ilum`. Pick canonical names here and
  make the shim + alert config match.
- **LAN addresses & firewall.** Port 8765 must be reachable on the LAN for the Mac Mini
  to poll each machine. Fill in addresses once assigned.
