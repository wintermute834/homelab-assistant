
from datetime import datetime, timezone

from harness import Harness
from llama_client import Tool

import time



# function definitions
def get_datetime_utc() -> str:
    time.sleep(1)
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_subagent(prompt: str) -> str:
    harness = Harness(*subagent_harness_params)
    response = harness.send_message(prompt)[-1]
    return response


def read_file(path: str) -> str:
    return """{"hostname":"rivendell","utc_timestamp":"2026-07-22T05:06:18Z","cpu":{"percent":0.1,"core_count":20,"load_avg_1m":0.1},"memory":{"total_gb":31.1,"used_gb":4.2,"percent":13.6},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":139.9,"percent":8.3}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":13507,"utilization_percent":0,"temperature_c":35},"network":{"interfaces":["eno0","wlp129s0","docker0","veth51a8f74"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"GPT-oss-20b","status":"unloaded","input_modalities":["text"]},{"name":"MiniCPM5-1B","status":"loaded","input_modalities":["text"]},{"name":"Nanbeige4.2-1B","status":"loaded","input_modalities":["text"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"loaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":160.9}"""



url = "http://192.168.0.210:8080"

tools = [
    Tool(**{
        "definition": {
            "function": {
                "name": "get_datetime_utc",
                "description": "Get the date and time at UTC-0."
            }
        },
        "function": get_datetime_utc
    }),
    Tool(**{
        "definition": {
            "function": {
                "name": "run_subagent",
                "description": "Runs a small LLM with the given prompt. They should NOT be used for anything requiring multi-step reasoning or specific knowledge. Subagents have the ability to read files. Tasks like data extraction from a file are ideal.",
                "parameters": {
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "The prompt the subagent will respond to."
                        }
                    },
                    "required": [
                        "prompt"
                    ]
                }
            }
        },
        "function": run_subagent
    }),
]

system_prompt = """
You are a homelab infrastructure assistant named Godzilla. Don't say your name unless the user asks for it.
You have access to real-time and historical data from four machines:
- rivendell (Linux, primary compute, RTX 5070 Ti GPU),
- ChibaCity (macOS, orchestration node),
- ilum (Windows 11, dev workstation),
- caladan (Linux, Santa Picker web host)

Current state data is provided as JSON. Answer questions factually based on this data.
If the data does not contain enough information to answer, say so - do not guess.
Keep responses concise.

Subagents can be used to extract specific facts from files.
Do not use subagents for any task that requires complex, multi-step reasoning.
Always double check that the subagent response makes sense and re-run the prompt if it seems like the subagent misunderstood.
Subagents don't have memory, every prompt will have none of the previous context from previous prompts.

All tool calls are run in parallel, so whenever you call tools call as many as possible.

Your location is Denver, CO

Current snapshot:
[{},{},{},{}]
"""


subagent_tools = None; [
    Tool(**{
        "definition": {
            "function": {
                "name": "read_file",
                "description": "Reads the text in a file.",
                "parameters": {
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read."
                        }
                    },
                    "required": [
                        "path"
                    ]
                }
            }
        },
        "function": read_file
    }),
]

subagent_system_prompt = """
You are an assistant to an AI model.
Answer questions clearly and concisely.
Only use tools if they are necessary.
Never ask follow up questions.
"""

subagent_harness_params = (
    "MiniCPM5-1B",
    subagent_tools,
    subagent_system_prompt,
    url
)

"""
Translate these sentences to english in paralell using subagents: 'Hola, mi nombre es Joe y me gusta el baloncesto', 'Mi equipo favorito son los Denver Nuggets y mi jugador favorito es Nikola Jokic', and 'Lamentablemente perdieron en la primera ronda de los playoffs este año, lo cual fue muy decepcionante'.
Translate these sentences to english: 'Hola, mi nombre es Joe y me gusta el baloncesto', 'Mi equipo favorito son los Denver Nuggets y mi jugador favorito es Nikola Jokic', and 'Lamentablemente perdieron en la primera ronda de los playoffs este año, lo cual fue muy decepcionante'.
"""


harness = Harness("Qwen3.5-4B", tools, system_prompt, url)

while True:
    prompt = input("User: ")

    match prompt:
        case "/exit":
            print("Exiting...")
            exit()
            
        case "/clear":
            print("Clearing memory...")
            harness.clear_history()

        case _:
            responses = harness.send_message(prompt)

            for line in responses:
                print(line)

