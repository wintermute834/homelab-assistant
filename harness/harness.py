
import json
import concurrent.futures as futures
from typing import Optional

from llama_client import LlamaClient
from llama_client.types.json import JSONObject
from llama_client.types.messages import Message, SystemMessage, ToolResponseMessage, UserMessage
from llama_client.types.query import Query
from llama_client.types.tool_calls import ToolCall
from llama_client.types.tool_defs import Tool



class ToolMap:
    __slots__ = "map"

    def __init__(self, tools: list[Tool]) -> None:
        self.map = {tool.definition.function.name: tool.function for tool in tools}
    
    def get_tool_response(self, tool_call: ToolCall) -> ToolResponseMessage:
        func = self.map.get(tool_call.function.name)

        if func is None:
            return ToolResponseMessage(
                content = f"Invalid tool: {tool_call.function.name}",
                id = tool_call.id
            )

        args: JSONObject = json.loads(tool_call.function.arguments)
        result = func(**args)

        return ToolResponseMessage(
            content = f"{{\"result\": \"{result}\"}}",
            id = tool_call.id
        )



class Harness:
    __slots__ = "client", "model", "tools", "tool_map", "messages", "system_prompt"

    def __init__(
            self,
            model: str,
            tools: Optional[list[Tool]] = None,
            system_prompt: Optional[str] = None,
            url: Optional[str] = None
        ) -> None:

        self.client = LlamaClient(url)

        self.model = model
        self.tools = tools
        self.tool_map = ToolMap(tools or [])
        self.messages: list[Message] = []
        self.system_prompt = system_prompt

        if system_prompt is not None:
            self.messages.append(SystemMessage(content = system_prompt))

    def send_message(self, user_message: str) -> list[str]:
        out = []

        self.messages.append(UserMessage(
            content = user_message
        ))

        while True:
            server_response = self.client.query(Query(
                model = self.model,
                tools = [tool.definition for tool in self.tools] if self.tools is not None else None,
                messages = self.messages
            ))

            response = server_response.choices[0]
            message = response.message

            out.append(f"Reasoning: {message.reasoning_content}")

            self.messages.append(message)

            if response.finish_reason == "tool_calls" and message.tool_calls is not None:
                with futures.ThreadPoolExecutor() as executor:
                    tool_futures: list[tuple[ToolCall, futures.Future[ToolResponseMessage]]] = []

                    for tool_call in message.tool_calls:
                        future = executor.submit(self.tool_map.get_tool_response, tool_call)
                        tool_futures.append((tool_call, future))

                    for tool_call, future in tool_futures:
                        tool_response = future.result()

                        self.messages.append(tool_response)

                        out.append(f"Tool Call: {json.dumps({
                            "name": tool_call.function.name,
                            "args": tool_call.function.arguments,
                            "output": tool_response.content
                        })}")

            else:
                out.append(f"{message.content}")
                break

        return out

    def clear_history(self) -> None:
        if self.system_prompt is None:
            self.messages.clear()

        else:
            self.messages = self.messages[:1]

