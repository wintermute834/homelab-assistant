
from harness import Harness

from . import lan_addresses
from . import tools



MODEL = "Qwen3.5-4B"
SYSTEM_PROMPT = """
You are a homelab infrastructure assistant.
You have access to real-time and historical data from four machines:
- rivendell (Linux, primary compute, llama.cpp, RTX 5070 Ti GPU),
- ChibaCity (macOS, orchestration node),
- ilum (Windows 11, dev workstation),
- caladan (Linux, Santa Picker web host)

Current state data is provided as JSON. Answer questions factually based on this data.
If the data does not contain enough information to answer, say so - do not guess.

Current snapshot:
[{},{},{},{}]
"""
LLAMA_URL = "http://192.168.0.210:8080"



class Orchestrator:
    def __init__(self) -> None:
        self.harness = Harness(
            MODEL,
            tools.ALL,
            SYSTEM_PROMPT,
            LLAMA_URL
        )

