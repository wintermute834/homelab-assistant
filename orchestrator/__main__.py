"""
The cli for the orchestrator.
"""

import json

from orchestrator import Orchestrator



orchestrator = Orchestrator()



while True:
    prompt = input("USER:\n")

    match prompt:
        case "/exit":
            print("Exiting...")
            exit()
            
        case "/clear":
            print("Clearing memory...")
            orchestrator.harness.clear_history()

        case _:
            messages = orchestrator.harness.send_message(prompt)[1:] # remove user message

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
