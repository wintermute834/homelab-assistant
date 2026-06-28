# Next Steps

_Last updated: 2026-06-24_

## Where we are

- **M1 complete & verified.** The shim is built and runs on the local WSL2 dev box
  (`ilum`). `GET /state` returns schema-valid JSON; `GET /health` returns ok.
- `gpu` and `services.ollama` correctly degrade to `null` on machines without an
  NVIDIA GPU / Ollama (verified on `ilum`).
- Disk filter added: pseudo/virtual filesystems (squashfs, overlay, tmpfs, 9p,
  `/mnt/wsl`, `/snap`, `/var/lib/docker`) and duplicate devices are dropped, so
  `disk[0]` is a real volume and won't false-fire the disk-usage alert.

## What's built

```
home-assistant/
├── requirements.txt        # fastapi, uvicorn[standard], psutil, httpx (pynvml commented — rivendell only)
├── NEXT_STEPS.md           # this file
├── project-homelab-assistant.md
└── shim/
    ├── __init__.py
    ├── schema.py           # Snapshot contract as Pydantic models (enforced, not just documented)
    ├── collectors.py       # cpu/mem/disk/gpu/network/ollama collectors; degrade to null when absent
    ├── server.py           # FastAPI app: GET /state, GET /health
    └── README.md
```

Local env: `.venv/` in the project root (created with `python3 -m venv`; needed
`sudo apt install python3-venv python3-pip` first on this box).

To re-run locally:
```bash
.venv/bin/uvicorn shim.server:app --host 0.0.0.0 --port 8765 --log-level warning
curl -s http://localhost:8765/state | python3 -m json.tool
```

## NEXT: Deploy + test shim on rivendell (M2)

User is doing this deploy **manually**.

### Getting the files onto the target

Pick one of these. **git clone is preferred** — it copies exactly the tracked files
(no `.venv`, no `__pycache__`, no `.lan_addresses.md`, since all are gitignored) and
updates later are a one-line `git pull`.

**Option A — git clone (preferred).** Repo is private (`cocteau834/homelab-assistant`),
so the target needs read access. Easiest is the GitHub CLI; an HTTPS token or deploy key
also works.
```bash
# one-time on the target, if gh isn't set up:
gh auth login                      # or use a token / SSH deploy key instead
gh repo clone cocteau834/homelab-assistant ~/homelab-shim
cd ~/homelab-shim
```
To update the shim on a later change, just: `cd ~/homelab-shim && git pull`.

The repo root has more than the shim (docs etc.), but that's harmless — you still only
*run* `shim/`, and `pip install -r requirements.txt` pulls just what the shim needs.

**Option B — copy only the shim (no git on the target).** Excludes `__pycache__` and the
shim README so only runtime files land:
```bash
rsync -av --exclude='__pycache__' --exclude='README.md' shim requirements.txt rivendell:~/homelab-shim/
```
Required runtime files: `shim/__init__.py`, `shim/schema.py`, `shim/collectors.py`,
`shim/server.py`, and `requirements.txt`. **Never** copy `.venv/` between machines —
recreate it per-target (next step).

### Then, on the target

1. (files are now in `~/homelab-shim` via Option A or B)
2. **Set up env on rivendell:**
   ```bash
   cd ~/homelab-shim
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   pip install pynvml          # rivendell ONLY — lights up the GPU field
   ```
3. **Sanity-check NVML before running:**
   ```bash
   python -c "import pynvml; pynvml.nvmlInit(); h=pynvml.nvmlDeviceGetHandleByIndex(0); print(pynvml.nvmlDeviceGetName(h))"
   ```
   Expect: `NVIDIA GeForce RTX 5070 Ti`.
4. **Run:** `uvicorn shim.server:app --host 0.0.0.0 --port 8765 --log-level warning`
5. **Test:** `curl -s http://localhost:8765/state | python3 -m json.tool`

### Validate in the output (this is the real M2 check)
- `gpu` → name, `memory_used_mb`, `utilization_percent`, `temperature_c` all populated (NOT null)
- `services.ollama` → `running: true`; `models_available` lists installed models
  (`qwen2.5:3b`, `qwen2.5-coder:14b`). `models_loaded` may be empty if nothing is
  currently resident in memory — that's expected, not a failure.
- `disk` → real volumes only, no snap/loop noise
- `hostname` → `rivendell`

## Known open questions / likely follow-ups

- **Ollama endpoint choice.** ✅ RESOLVED — `collect_ollama()` now reports both
  `models_available` (installed, via `/api/tags`) and `models_loaded` (in memory, via
  `/api/ps`), with `/api/tags` as the liveness signal. M2 should confirm both fields
  look right on rivendell.
- **Firewall.** When the Mac Mini orchestrator later polls rivendell, port 8765 must
  be open on the LAN. Not needed for local-only testing.
- **Persistence.** Currently hand-launched. For unattended running (M7 goal),
  wrap in a systemd unit later. User opted for manual launch for now.

## After M2

- M2: shims on all three machines (Mac Mini, Windows box next).
- M3: Mac Mini orchestrator — polling loop + SQLite history store.
