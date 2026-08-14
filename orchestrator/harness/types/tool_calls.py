"""
Pydantic models for model tool calling.
"""

from typing import Literal

from pydantic import BaseModel



class CallFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    type: Literal["function"] = "function"
    function: CallFunction
    id: str
