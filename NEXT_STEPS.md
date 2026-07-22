# Next Steps

_Last updated: 2026-06-28_

## Where we are

- **Repo is on GitHub** (private): `wintermute834/homelab-assistant`, default branch
  `main`. LAN addresses kept out via gitignored `.lan_addresses.md`. A son account was
  added as a collaborator via the web portal.
- **M1 complete & verified.** The shim is built and runs on the local WSL2 dev box
  (`ilum`). `GET /state` returns schema-valid JSON; `GET /health` returns ok.
- `gpu` and `services.llamacpp` correctly degrade to `null` on machines without an
  NVIDIA GPU / llama.cpp (verified on `ilum`).
- Disk filter added: pseudo/virtual filesystems (squashfs, overlay, tmpfs, 9p,
  `/mnt/wsl`, `/snap`, `/var/lib/docker`) and duplicate devices are dropped, so
  `disk[0]` is a real volume and won't false-fire the disk-usage alert.

## What's built

```
home-assistant/
├── requirements.txt        # fastapi, uvicorn[standard], psutil, httpx (pynvml commented - rivendell only)
├── NEXT_STEPS.md           # this file
├── project-homelab-assistant.md
└── shim/
    ├── __init__.py
    ├── schema.py           # Snapshot contract as Pydantic models (enforced, not just documented)
    ├── collectors.py       # cpu/mem/disk/gpu/network/llamacpp collectors; degrade to null when absent
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

## DONE: Deploy + test shim on rivendell (M2)

User is doing this deploy **manually**.

### Getting the files onto the target

Pick one of these. **git clone is preferred** - it copies exactly the tracked files
(no `.venv`, no `__pycache__`, no `.lan_addresses.md`, since all are gitignored) and
updates later are a one-line `git pull`.

**Option A - git clone (preferred).** Repo is private (`wintermute834/homelab-assistant`),
so the target needs read access. Easiest is the GitHub CLI; an HTTPS token or deploy key
also works.
```bash
# one-time on the target, if gh isn't set up:
gh auth login                      # or use a token / SSH deploy key instead
gh repo clone wintermute834/homelab-assistant ~/homelab-shim
cd ~/homelab-shim
```
To update the shim on a later change, just: `cd ~/homelab-shim && git pull`.

The repo root has more than the shim (docs etc.), but that's harmless - you still only
*run* `shim/`, and `pip install -r requirements.txt` pulls just what the shim needs.

**Option B - copy only the shim (no git on the target).** Excludes `__pycache__` and the
shim README so only runtime files land:
```bash
rsync -av --exclude='__pycache__' --exclude='README.md' shim requirements.txt rivendell:~/homelab-shim/
```
Required runtime files: `shim/__init__.py`, `shim/schema.py`, `shim/collectors.py`,
`shim/server.py`, and `requirements.txt`. **Never** copy `.venv/` between machines -
recreate it per-target (next step).

### Then, on the target

1. (files are now in `~/homelab-shim` via Option A or B)
2. **Set up env on rivendell:**
   ```bash
   cd ~/homelab-shim
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   pip install pynvml          # rivendell ONLY - lights up the GPU field
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
- `services.llama_cpp` → `running: true`; `models` lists installed models
  (`Qwen3.5-4B`, `Qwen3.5-Mythos-9B`) and their status/capabilities
- `disk` → real volumes only, no snap/loop noise
- `hostname` → `rivendell`

## Known open questions / likely follow-ups

- **llama.cpp endpoint choice.** ✅ RESOLVED - `collect_llama()` now reports
  `model` (installed, via `/models`) with status and capabilities
- **Firewall.** When the Mac Mini orchestrator later polls rivendell, port 8765 must
  be open on the LAN. Not needed for local-only testing.
- **Persistence.** Currently hand-launched. For unattended running (M7 goal),
  wrap in a systemd unit later. User opted for manual launch for now.

## NEXT: After M2

- M2: shims on the rest of the fleet (now **4 machines** - rivendell, caladan, the Mac
  Mini `ChibaCity`, and the dev box `ilum`; see `machines.md`).
- M3: Mac Mini orchestrator - polling loop + SQLite history store.
