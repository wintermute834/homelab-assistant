
from datetime import datetime, timezone

from harness import Harness
from llama_client.llama_client import LlamaClient
from llama_client.types.tool_defs import Tool



# function definitions
def get_datetime_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_subagent(prompt: str) -> str:
    return subagent_client.get_response("Qwen3.5-4B", prompt)


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
                "description": "Runs a small LLM with the given prompt. Subagent doesn't have tool access and should only be used for small tasks.",
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
You are a homelab infrastructure assistant. You have no name and no creator. You have access to real-time and historical
data from four machines:
  rivendell (Linux, primary compute, RTX 5070 Ti GPU),
  ChibaCity (macOS, orchestration node),
  ilum (Windows 11, dev workstation),
  caladan (Linux, Santa Picker web host)

Current state data is provided as JSON. Answer questions factually based on this data.
If the data does not contain enough information to answer, say so - do not guess.
Keep responses concise.

Current snapshot:
[{},{},{},{}]
"""

"""
Translate these sentences to english in paralell using subagents: 'Hola, mi nombre es Joe y me gusta el baloncesto', 'Mi equipo favorito son los Denver Nuggets y mi jugador favorito es Nikola Jokic', and 'Lamentablemente perdieron en la primera ronda de los playoffs este año, lo cual fue muy decepcionante'.
"""

url = "http://192.168.0.210:8080"

subagent_client = LlamaClient(url)

harness = Harness("Qwen3.5-4B", tools, system_prompt, url)

while True:
    prompt = input("User: ")

    if prompt == "/exit":
        print("Exiting...")
        exit()
    
    responses = harness.send_message(prompt)

    for line in responses:
        print(line)
