# Next Steps

*Last updated: 2026-08-15*

## Where we are

- `homelab-shim` and `homelab-assistant` repos are on GitHub, both private.
- **M1 and M2 complete** - Shim works on all machines.
- **M3 complete but needs changes** - Orchestrator works on *ChibaCity* (but not persistent as a services)
  Orchestrator collects snapshots and stores them, collection will be changed to a separate service
- **M4 complete.** - LLM queries working in a CLI chat loop with multi-turn tool use.
  - `get_newest_snapshots` - latest snapshot from each machine
  - `filter_snapshots` - historical snapshots by hostname + UTC timestamp range (M6 building block)
  - `get_datetime_utc` - current UTC time, so the model can resolve "last night"
- **M7 partially complete** - Shims for *rivendell* and *caladan* run automatically and survive restarts

To run the shim manually:
```bash
uvicorn server:app --host 0.0.0.0 --port 8765
```

To run the orchestrator manually:
```bash
python -m orchestrator
```

## Checkpoints left

- **M3** - Snapshot collection needs to be split into a separate service.
  Orchestrator can then be a manually run chat interface that only worries about llm inference, tool calls, and reading database.
  Snapshot collection speed should also be ser per-machine for more fine-grained analysis during training runs, etc.
- **M5** - Alert rule engine
  Not started
  Rules can be checked after each round of new snapshots are added.
- **M6** - History-based queries
  Mostly working but needs refinement with respect to date and time in local timezone.
  Filtering could also have more options and be explained to the LLM more clearly.
  Upgrading historic data requests to a bigger model might be required, as `LFM2.5-2.6B` might not be able to handle timestamp range math and large json dumps.
- **M7** - Run unattended
  Shim services exist for *rivendell* and *caladan* (systemd).
  *ChibaCity's* shim + orchestrator  are currently manual and need launchd units
  *ilum's* shim isn't set up
  30-day retention of `snapshots.db` should be enforced.

## Other todos

- **Santa picker** - add a service for the santa picker so questions regarding its status/downtimes can be answered
- **Check firewall** - When the orchestrator polls each shim, port 8765 must be open on the LAN.
- **Separate snapshot collection** - Split the snapshot collection into a service of its own so it can always run
  and the orchestrator can be something manually launched when needed, like a chat terminal (part of M3).
- **New models** - New models may be available that are better suited to the tasks
  - `MiniCPM5-1B` - Tiny subagent tasks (likely won't be used; could do image analysis for larger models, which this model can't do)
  - `LFM2.5-2.6B` - Simple chatting w/ tool calling
  - `Qwen3.5-9B` - Snapshot log filtering and analysis and lighter coding
  - `Qwen3.8-27B` - Complex coding
- **Local coding assistant** - Could be added on to the homelab-assistant
