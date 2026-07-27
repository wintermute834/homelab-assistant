
from datetime import datetime, timezone
import json

import orchestrator.tools
from harness import Harness
from llama_client import Tool



# function definitions
def get_datetime_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_subagent(prompt: str) -> str:
    harness = Harness(*subagent_harness_params)
    response = harness.send_message(prompt)[-1].content
    return response


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
                "description": "Runs a small LLM with the given prompt. They should NOT be used for anything requiring multi-step reasoning or specific knowledge.",
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
You are a helpful AI assistant.
"""
# system_prompt = """
# You are a homelab infrastructure assistant.
# You have access to real-time and historical data from four machines:
# - rivendell (Linux, primary compute, RTX 5070 Ti GPU),
# - ChibaCity (macOS, orchestration node),
# - ilum (Windows 11, dev workstation),
# - caladan (Linux, Santa Picker web host)

# Current state data is provided as JSON. Answer questions factually based on this data.
# If the data does not contain enough information to answer, say so - do not guess.
# Keep responses concise.

# Do not use subagents for any task that requires complex, multi-step reasoning.
# Always double check that the subagent response makes sense and re-run the prompt if it seems like the subagent misunderstood.
# Subagents don't have memory, every prompt will have none of the previous context from previous prompts.

# All tool calls are run in parallel, so whenever you call tools call as many as possible.

# Your location is Denver, CO

# Current snapshot:
# [{},{},{},{}]
# """

subagent_system_prompt = """
You are an assistant to an AI model.
Answer questions clearly and concisely.
Never ask follow up questions.
"""

subagent_harness_params = (
    "MiniCPM5-1B",
    None,
    subagent_system_prompt,
    url
)

_test_prompts = """
Translate these sentences to english in paralell using subagents: 'Hola, mi nombre es Joe y me gusta el baloncesto', 'Mi equipo favorito son los Denver Nuggets y mi jugador favorito es Nikola Jokic', and 'Lamentablemente perdieron en la primera ronda de los playoffs este año, lo cual fue muy decepcionante'.

Start multiple subagents and ask them the what capital of each country is: Egypt, Estonia, Belarus, Singapore, China, United States, and Finland. Return their results.

Read the readme and explain the project.

Explore every python module in the environment using list_dir and read_file and report back with your findings. Ignore the .venv modules.
"""


harness = Harness("Qwen3.5-9B", [orchestrator.tools.get_datetime_utc], system_prompt, url)

while True:
    prompt = input("USER:\n")
    print("\n")

    match prompt:
        case "/exit":
            print("Exiting...")
            exit()
            
        case "/clear":
            print("Clearing memory...")
            harness.clear_history()

        case _:
            messages = harness.send_message(prompt)[1:] # remove user message

            for message in messages:
                match message.role:
                    case "system":
                        print(f"SYSTEM:\n{message.content}\n")

                    case "assistant":
                        if message.reasoning_content is not None:
                            print(f"REASONING:\n{message.reasoning_content}\n")
                            
                        if message.tool_calls is not None:
                            for tool_call in message.tool_calls:
                                tool_call_repr = json.dumps({
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                    "id": tool_call.id
                                }, indent=2, ensure_ascii=False)

                                print(f"TOOL CALL: {tool_call_repr}\n")

                        if message.content != "":
                            print(f"ASSISTANT:\n{message.content}\n")

                    case "tool":
                        tool_response_repr = json.dumps({
                            "content": message.content,
                            "id": message.id
                        }, indent=2, ensure_ascii=False)

                        print(f"TOOL RESPONSE: {tool_response_repr}\n")

                    case "user":
                        print(f"ERROR !!! USER INPUT INCLUDED")

