
import json

from orchestrator import tools
from harness import Harness
from lan_addresses import LLAMA_URL



system_prompt = """
You are a homelab infrastructure assistant.
You have access to real-time and historical data from two machines:
- rivendell (Linux, primary compute, RTX 5070 Ti GPU)
- Joe (Windows 11, dev workstation)

State data is provided as JSON. Answer questions factually based on this data.
If the data does not contain enough information to answer, say so, do not guess.
Keep responses concise.

Snapshots:
[('{"hostname":"Joe","utc_timestamp":"2026-07-28T01:28:49Z","cpu":{"load":8.9,"core_count":12,"load_avg_1m":0.0},"memory":{"total_gb":31.1,"used_gb":11.4,"used_percent":36.6},"disk":[{"mount":"C:\\\\","total_gb":930.7,"used_gb":315.6,"used_percent":33.9},{"mount":"D:\\\\","total_gb":1862.5,"used_gb":38.8,"used_percent":2.1}],"gpu":null,"network":{"interfaces":["Ethernet","vEthernet (WSL (Hyper-V firewall))","Loopback Pseudo-Interface 1","Wi-Fi 2","Local Area Connection* 11","Local Area Connection* 12"],"reachable":true},"services":{"llama_cpp":null},"uptime_hours":243.4}',), ('{"hostname":"rivendell","utc_timestamp":"2026-07-28T01:28:44Z","cpu":{"load":0.0,"core_count":20,"load_avg_1m":0.0},"memory":{"total_gb":31.1,"used_gb":1.8,"used_percent":5.7},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":146.2,"used_percent":8.7}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":465,"utilization_percent":0,"temperature_c":40},"network":{"interfaces":["eno0","wlp129s0","docker0","vethc9de0fc"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"MiniCPM5-1B","status":"unloaded","input_modalities":["text"]},{"name":"Nanbeige4.2-3B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-0.8B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":97.7}',), ('{"hostname":"Joe","utc_timestamp":"2026-07-28T01:26:16Z","cpu":{"load":5.9,"core_count":12,"load_avg_1m":0.0},"memory":{"total_gb":31.1,"used_gb":13.0,"used_percent":41.8},"disk":[{"mount":"C:\\\\","total_gb":930.7,"used_gb":315.6,"used_percent":33.9},{"mount":"D:\\\\","total_gb":1862.5,"used_gb":38.8,"used_percent":2.1}],"gpu":null,"network":{"interfaces":["Ethernet","vEthernet (WSL (Hyper-V firewall))","Loopback Pseudo-Interface 1","Wi-Fi 2","Local Area Connection* 11","Local Area Connection* 12"],"reachable":true},"services":{"llama_cpp":null},"uptime_hours":243.4}',), ('{"hostname":"rivendell","utc_timestamp":"2026-07-28T01:26:11Z","cpu":{"load":0.1,"core_count":20,"load_avg_1m":0.1},"memory":{"total_gb":31.1,"used_gb":1.8,"used_percent":5.7},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":146.2,"used_percent":8.7}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":465,"utilization_percent":0,"temperature_c":40},"network":{"interfaces":["eno0","wlp129s0","docker0","vethc9de0fc"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"MiniCPM5-1B","status":"unloaded","input_modalities":["text"]},{"name":"Nanbeige4.2-3B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-0.8B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":97.7}',), ('{"hostname":"Joe","utc_timestamp":"2026-07-28T01:25:31Z","cpu":{"load":5.6,"core_count":12,"load_avg_1m":0.0},"memory":{"total_gb":31.1,"used_gb":13.2,"used_percent":42.5},"disk":[{"mount":"C:\\\\","total_gb":930.7,"used_gb":315.6,"used_percent":33.9},{"mount":"D:\\\\","total_gb":1862.5,"used_gb":38.8,"used_percent":2.1}],"gpu":null,"network":{"interfaces":["Ethernet","vEthernet (WSL (Hyper-V firewall))","Loopback Pseudo-Interface 1","Wi-Fi 2","Local Area Connection* 11","Local Area Connection* 12"],"reachable":true},"services":{"llama_cpp":null},"uptime_hours":243.3}',), ('{"hostname":"rivendell","utc_timestamp":"2026-07-28T01:25:26Z","cpu":{"load":0.0,"core_count":20,"load_avg_1m":0.2},"memory":{"total_gb":31.1,"used_gb":1.8,"used_percent":5.7},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":146.2,"used_percent":8.7}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":465,"utilization_percent":0,"temperature_c":40},"network":{"interfaces":["eno0","wlp129s0","docker0","vethc9de0fc"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"MiniCPM5-1B","status":"unloaded","input_modalities":["text"]},{"name":"Nanbeige4.2-3B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-0.8B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":97.7}',), ('{"hostname":"Joe","utc_timestamp":"2026-07-28T01:23:34Z","cpu":{"load":0.0,"core_count":12,"load_avg_1m":0.0},"memory":{"total_gb":31.1,"used_gb":13.3,"used_percent":42.7},"disk":[{"mount":"C:\\\\","total_gb":930.7,"used_gb":315.5,"used_percent":33.9},{"mount":"D:\\\\","total_gb":1862.5,"used_gb":38.8,"used_percent":2.1}],"gpu":null,"network":{"interfaces":["Ethernet","vEthernet (WSL (Hyper-V firewall))","Loopback Pseudo-Interface 1","Wi-Fi 2","Local Area Connection* 11","Local Area Connection* 12"],"reachable":true},"services":{"llama_cpp":null},"uptime_hours":243.3}',), ('{"hostname":"rivendell","utc_timestamp":"2026-07-28T01:23:29Z","cpu":{"load":0.0,"core_count":20,"load_avg_1m":0.2},"memory":{"total_gb":31.1,"used_gb":1.8,"used_percent":5.7},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":146.2,"used_percent":8.7}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":465,"utilization_percent":0,"temperature_c":40},"network":{"interfaces":["eno0","wlp129s0","docker0","vethc9de0fc"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"MiniCPM5-1B","status":"unloaded","input_modalities":["text"]},{"name":"Nanbeige4.2-3B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-0.8B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":97.7}',), ('{"hostname":"rivendell","utc_timestamp":"2026-07-28T01:23:05Z","cpu":{"load":0.0,"core_count":20,"load_avg_1m":0.4},"memory":{"total_gb":31.1,"used_gb":1.8,"used_percent":5.7},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":146.2,"used_percent":8.7}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":465,"utilization_percent":0,"temperature_c":40},"network":{"interfaces":["eno0","wlp129s0","docker0","vethc9de0fc"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"MiniCPM5-1B","status":"unloaded","input_modalities":["text"]},{"name":"Nanbeige4.2-3B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-0.8B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":97.6}',), ('{"hostname":"rivendell","utc_timestamp":"2026-07-28T01:21:47Z","cpu":{"load":0.0,"core_count":20,"load_avg_1m":0.1},"memory":{"total_gb":31.1,"used_gb":1.8,"used_percent":5.7},"disk":[{"mount":"/","total_gb":1688.0,"used_gb":146.2,"used_percent":8.7}],"gpu":{"name":"NVIDIA GeForce RTX 5070 Ti","memory_total_mb":16303,"memory_used_mb":465,"utilization_percent":0,"temperature_c":40},"network":{"interfaces":["eno0","wlp129s0","docker0","vethc9de0fc"],"reachable":true},"services":{"llama_cpp":{"running":true,"models":[{"name":"MiniCPM5-1B","status":"unloaded","input_modalities":["text"]},{"name":"Nanbeige4.2-3B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-0.8B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.5-4B","status":"unloaded","input_modalities":["text"]},{"name":"Qwen3.5-9B","status":"unloaded","input_modalities":["text","image"]},{"name":"Qwen3.6-27B","status":"unloaded","input_modalities":["text"]}]}},"uptime_hours":97.6}',)]
"""
# system_prompt = """
# You are a homelab infrastructure assistant.
# You have access to real-time and historical data from four machines:
# - rivendell (Linux, primary compute, RTX 5070 Ti GPU)
# - ChibaCity (macOS, orchestration node)
# - ilum (Windows 11, dev workstation)
# - caladan (Linux, Santa Picker web host)

# Current state data is provided as JSON. Answer questions factually based on this data.
# If the data does not contain enough information to answer, say so - do not guess.
# Keep responses concise.

# Do not use subagents for any task that requires complex, multi-step reasoning.
# Always double check that the subagent response makes sense and re-run the prompt if it seems like the subagent misunderstood.
# Subagents don't have memory, every prompt will have none of the previous context from previous prompts.

# All tool calls are run in parallel, so whenever you call tools call as many as possible.

# Current snapshot:
# [{},{},{},{}]
# """

_test_prompts = """
Translate these sentences to english in paralell using subagents: 'Hola, mi nombre es Joe y me gusta el baloncesto', 'Mi equipo favorito son los Denver Nuggets y mi jugador favorito es Nikola Jokic', and 'Lamentablemente perdieron en la primera ronda de los playoffs este año, lo cual fue muy decepcionante'.

Start multiple subagents and ask them the what capital of each country is: Egypt, Estonia, Belarus, Singapore, China, United States, and Finland. Return their results.

Read the readme and explain the project.

Explore every python module in the environment using list_dir and read_file and report back with your findings. Ignore the .venv modules.

I am updating the codebase in your current directory. I want you to recursively search the directory for all python files and then for each file start a subagent that has the prompt: "update the python file {exact file path} to have documentation for all classes and functions. Additionally, add/update the __slots__ for all non-pydantic classes to have the correct attribute names." Give subagents access to all file-editing tools.
"""

# model = "LFM2.5-2.6B"
# model = "Qwen3.5-4B"
model = "Qwen3.5-9B"
harness = Harness(model, tools.file_tools + (tools.get_datetime_utc, tools.query_subagent), system_prompt, LLAMA_URL)

while True:
    prompt = input("USER:\n")

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

