
from datetime import datetime, timezone
from typing import Optional

from lan_addresses import LLAMA_URL

from .files import *
from ..harness import Harness, Tool



__all__ = (
    "get_datetime_utc",
    "query_subagent",
    "misc_tools"
)



# Tool functions
def _get_datetime_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _query_subagent(*, prompt: str, tool_names: Optional[list[str]] = None) -> str:
    tools: Optional[list[Tool]] = None

    if tool_names:
        tools = []
        invalid_tools: list[str] = []

        for name in tool_names:
            if name in TOOL_MAP:
                tools.append(TOOL_MAP[name])

            else:
                invalid_tools.append(name)

        if invalid_tools:
            return f"Invalid tool names provided to subagent: {", ".join(invalid_tools)}"

    harness = Harness(
        SUBAGENT_MODEL,
        tools,
        None,
        LLAMA_URL
    )

    response = harness.send_message(prompt)[-1].content
    return response


# Tool definiitons
get_datetime_utc = Tool(**{
    "definition": {
        "function": {
            "name": "get_datetime_utc",
            "description": "Get the date and time at UTC-0."
        }
    },
    "function": _get_datetime_utc
})

query_subagent = Tool(**{
    "definition": {
        "function": {
            "name": "query_subagent",
            "description": "Runs a small LLM with the given prompt and access to the given tools and returns its response. Subagents don't have memory of any previous queries and should not be used for anything requiring multi-step reasoning or specific knowledge, unless provided.",
            "parameters": {
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The prompt the subagent will respond to."
                    },
                    "tool_names": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "The names of the tools the subagent can use. Can include any tools you have access to except query_subagent. Be cautious with providing file editing privileges to subagents. By default, the subagent has access to no tools."
                    }
                },
                "required": [
                    "prompt"
                ]
            }
        }
    },
    "function": _query_subagent
})


# Map str to tools. Used for assigning subagents tools
TOOL_MAP = {
    "get_datetime_utc": get_datetime_utc,
    "list_dir": list_dir,
    "read_file": read_file,
    "create_file": create_file,
    "write_file": write_file,
    "append_file": append_file,
    "replace_file": replace_file
}

SUBAGENT_MODEL = "LFM2.5-2.6B"


# Collection of all misc tools
misc_tools = (
    "get_datetime_utc",
    "query_subagent"
)

