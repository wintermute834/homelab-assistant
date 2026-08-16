"""
The cli for the orchestrator.
"""

import json

from orchestrator import Orchestrator



orchestrator = Orchestrator()

show_reasoning_tools = False


print("""

--------- Homelab Assistant ----------

A CLI chat with the homelab assistant.

Commands:
/exit --- ends the conversation
/clear -- clears the agent's memory
          basically starts a new convo
/toggle - toggles reasoning/tool visibility
          default off

--------- Conversation Start ---------

""")


while True:
    prompt = input("USER:\n\n")

    match prompt:
        case "/exit":
            print("Exiting...")
            exit()

        case "/clear":
            orchestrator.harness.clear_history()
            print("Memory cleared...")

        case "/toggle":
            show_reasoning_tools = not show_reasoning_tools
            print(f"Reasoning and tool calls turned {"ON" if show_reasoning_tools else "OFF"}!\n")

        case _:
            messages = orchestrator.harness.send_message(prompt)

            for message in messages:
                match message.role:
                    case "system":
                        print(f"SYSTEM:\n{message.content}\n")

                    case "assistant":
                        if message.reasoning_content is not None and show_reasoning_tools:
                            print(f"REASONING:\n{message.reasoning_content}\n")

                        if message.content != "":
                            print(f"ASSISTANT:\n{message.content}\n")

                        if message.tool_calls is not None and show_reasoning_tools:
                            for tool_call in message.tool_calls:
                                tool_call_repr = json.dumps({
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments,
                                    "id": tool_call.id
                                }, indent=2, ensure_ascii=False)

                                print(f"TOOL CALL: {tool_call_repr}\n")

                    case "tool":
                        tool_response_repr = json.dumps({
                            "content": message.content,
                            "id": message.id
                        }, indent=2, ensure_ascii=False)

                        print(f"TOOL RESPONSE: {tool_response_repr}\n")

                    case "user":
                        # should only trigger for max tool use turns
                        print(f"USER: {message.content}\n")
