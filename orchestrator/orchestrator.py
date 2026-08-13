"""
The orchestrator for the system.

Collects snapshots every minute and 
"""

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

Snapshots are formatted in json and have the following information:
- Hostname
- UTC-0 timestamp
- CPU
  - Core count
  - Load
- Memory (RAM)
  - Capacity
  - Usage
- Disks (list of SSD and hard drives)
  - mount name ("/", "C:\\")
  - Capacity
  - Usage
- GPU (on some systems)
  - Name/manufacturer
  - memory capacity
  - memory usage
  - compute utilization
  - temperature
- Networks
  - List of interfaces
  - Availability
- Services
  - llama.cpp
    - Status
    - List of models including their name, status, and input modalities (text, image, audio, video)
  - Santa picker
    - Status
- Uptime

All percentages in snapshots are out of 100, so a value of 0.5 would mean 0.5% not 50%.
Snapshot data is collected every minute from each machine and can be accessed using tool calls.
When retrieving snapshots, always use the exact hostnames outlined above.
If the user asks about current information, always use `get_newest_snapshots`.
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
