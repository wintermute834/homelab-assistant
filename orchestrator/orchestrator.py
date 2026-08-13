
from threading import Event, Lock, Thread

from lan_addresses import *
from shim import get_shim

from . import tools
from .harness import Harness
from .database import SnapshotDatabase



COLLECTION_SEC = 60.0
MODEL = "LFM2.5-2.6B"
SYSTEM_PROMPT = """
You are a homelab infrastructure assistant.
You have access to real-time and historical data (snapshots) from four machines:
- rivendell (Linux, primary compute, llama.cpp, RTX 5070 Ti GPU),
- ChibaCity (macOS, orchestration node),
- ilum (Windows 11, dev workstation),
- caladan (Linux, Santa Picker web host)

Snapshot format with notes:
```jsonc
{
  "hostname": "rivendell",
  "utc_timestamp": "2026-08-13 07:51:19",    // At UTC-0 in "YYYY-MM-DD HH:MM:SS" format
  "cpu": {
    "core_count": 20,
    "load_percent": 0.5,    // All values labeled percent are out of 100.0. For example, this field is 0.5% not 50%
    "load_percent_avg_1m": 0.1
  },
  "memory": {    // RAM
    "total_gb": 31.1,
    "used_gb": 2.2,
    "used_percent": 7.0
  },
  "disk": [    // SSD and Hard drives
    {
      "mount": "/",
      "total_gb": 1688.0,
      "used_gb": 128.7,
      "used_percent": 7.6
    }
  ],
  "gpu": {
    "name": "NVIDIA GeForce RTX 5070 Ti",
    "memory_total_mb": 16303,
    "memory_used_mb": 724,
    "utilization_percent": 0,    // The utilization of GPU compute, not GPU VRAM
    "temperature_c": 40
  },
  "network": {
    "interfaces": [
      "eno0",
      "wlp129s0",
      "docker0",
      "vethfabe93b"
    ],
    "reachable": true
  },
  "services": {
    "llama_cpp": {
      "running": true,
      "models": [
        {
          "name": "LFM2.5-2.6B",
          "status": "sleeping",
          "input_modalities": [
            "text"
          ]
        },
        {
          "name": "MiniCPM5-1B",
          "status": "unloaded",
          "input_modalities": [
            "text"
          ]
        },
        {
          "name": "Qwen3.5-9B",
          "status": "unloaded",
          "input_modalities": [
            "text",
            "image"
          ]
        },
        {
          "name": "Qwen3.6-27B",
          "status": "unloaded",
          "input_modalities": [
            "text"
          ]
        }
      ]
    }
  },
  "uptime_hours": 488.0
}
```

Snapshot data is collected every minute from each machine and can be accessed using tool calls.
When retrieving snapshots, always use the exact hostnames outlined above.
If the data does not contain enough information to answer, say so - do not guess.

Your location is Denver, CO.

Never use markdown formatting in answers.
"""



class Orchestrator:
    __slots__ = "database", "_database_lock", "harness", "collection_stop", "collection_thread"

    def __init__(self) -> None:
        self.database = SnapshotDatabase()
        self._database_lock = Lock()

        self.harness = Harness(
            MODEL,
            tools.database_tools + (tools.get_datetime_utc,),
            SYSTEM_PROMPT,
            LLAMA_URL
        )

        self.start_collection()


    def start_collection(self) -> None:
        """
        Starts the collection loop.
        """

        self.collection_stop = Event()
        self.collection_thread = Thread(target=self._collector, daemon=True)
        self.collection_thread.start()


    def stop_collection(self) -> None:
        """
        Stops the collection loop.
        """

        self.collection_stop.set()


    def _collector(self) -> None:
        """
        A simple loop that runs collection for all shims simultaneously every `COLLECTION_SEC` seconds.
        
        Terminates immediately when `self.collection_stop` is set.
        """

        while not self.collection_stop.is_set():
            for url in SHIM_URLS:
                thread = Thread(target=self._collect, args=(url,), daemon=True)
                thread.start()

            self.collection_stop.wait(COLLECTION_SEC)


    def _collect(self, shim_url: str) -> None:
        """
        Collects the snapshot from the given url and inserts it in the database.
        """

        snapshot = get_shim(shim_url)

        if snapshot is not None:
            with self._database_lock:
                self.database.insert_snapshot(snapshot)
