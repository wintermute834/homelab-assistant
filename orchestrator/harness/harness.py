"""
An LLM harness that connects to llama.cpp.

Has multi-turn tool use, configurable system prompt, and optional reasoning trace removal.
"""

import json
import concurrent.futures as futures
from typing import Collection, Generator, Optional

from .llama_client import LlamaClient
from .types.json import JSONObject
from .types.messages import AssistantMessage, Message, SystemMessage, ToolResponseMessage, UserMessage
from .types.query import Query
from .types.tool_calls import ToolCall
from .types.tool_defs import Tool



class ToolMap:
    __slots__ = "map"

    def __init__(self, tools: Collection[Tool]) -> None:
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

        if isinstance(result, str):
            content = result

        else:
            content = json.dumps(result, ensure_ascii=False)

        return ToolResponseMessage(
            content = content,
            id = tool_call.id
        )



class Harness:
    __slots__ = "client", "model", "tools", "tool_map", "messages", "system_message", "keep_reasoning", "max_tool_turns"

    def __init__(
            self,
            model: str,
            tools: Optional[Collection[Tool]] = None,
            system_prompt: Optional[str] = None,
            url: Optional[str] = None,
            keep_reasoning: bool = False,
            max_tool_turns: Optional[int] = None
        ) -> None:

        self.client = LlamaClient(url)

        self.model = model
        self.tools = tools
        self.tool_map = ToolMap(tools or [])
        self.messages: list[Message] = []
        self.system_message = SystemMessage(content=system_prompt) if system_prompt is not None else None
        self.keep_reasoning = keep_reasoning
        self.max_tool_turns = max_tool_turns

        self.clear_history()


    def send_message(self, user_message: str) -> Generator[Message]:
        self.messages.append(UserMessage(content = user_message))

        start_index = len(self.messages)
        turns = 0

        while self.max_tool_turns is None or turns < self.max_tool_turns:
            server_response = self.client.query(Query(
                model = self.model,
                tools = [tool.definition for tool in self.tools] if self.tools is not None else None,
                messages = self.messages
            ))
            response = server_response.choices[0]
            message = response.message

            self.messages.append(message)
            yield message

            if response.finish_reason == "tool_calls" and message.tool_calls is not None:
                with futures.ThreadPoolExecutor() as executor:
                    tool_futures: list[tuple[ToolCall, futures.Future[ToolResponseMessage]]] = []

                    # start parallel futures for all tool calls
                    for tool_call in message.tool_calls:
                        future = executor.submit(self.tool_map.get_tool_response, tool_call)
                        tool_futures.append((tool_call, future))

                    # wait until all futures are done, adding them as they finish
                    for tool_call, future in tool_futures:
                        tool_response = future.result()

                        self.messages.append(tool_response)
                        yield tool_response

            else:
                break

            turns += 1

        else:
            # If tool uses reaches maximum, terminates and adds a message then forces the model to answer without tools
            out_of_tools_message = UserMessage(content=f"You have reached the maximum number of tool calls ({self.max_tool_turns}) for this turn. Provide your final answer without any more tool calls.")
            self.messages.append(out_of_tools_message)
            yield out_of_tools_message

            server_response = self.client.query(Query(
                model = self.model,
                tools = None,
                messages = self.messages
            ))
            response = server_response.choices[0]
            message = response.message

            self.messages.append(message)
            yield message

        # remove reasoning from assistant messages if self.keep_reasoning is False
        if not self.keep_reasoning:
            for i, message in enumerate(self.messages[start_index:], start_index):
                if isinstance(message, AssistantMessage):
                    self.messages[i] = message.without_reasoning()


    def clear_history(self) -> None:
        self.messages.clear()

        if self.system_message is not None:
            self.messages.append(self.system_message)
