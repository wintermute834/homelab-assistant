
from database import SnapshotDatabase
from harness import Harness

from lan_addresses import *
from . import tools



MODEL = "LFM2.5-2.6B"
SYSTEM_PROMPT = """
You are a homelab infrastructure assistant.
You have access to real-time and historical data from four machines:
- rivendell (Linux, primary compute, llama.cpp, RTX 5070 Ti GPU),
- ChibaCity (macOS, orchestration node),
- ilum (Windows 11, dev workstation),
- caladan (Linux, Santa Picker web host)

State data can be retrieved using tool calls, and is returned as JSON data.
When retrieving state data, always use the exact hostnames outlined above.
If the data does not contain enough information to answer, say so - do not guess.

Your location is Denver, CO.

Don't use markdown formatting when answering.
"""



class Orchestrator:
    def __init__(self) -> None:
        self.database = SnapshotDatabase()

        self.harness = Harness(
            MODEL,
            [tools.get_datetime_utc, tools.get_snapshots],
            SYSTEM_PROMPT,
            LLAMA_URL
        )


