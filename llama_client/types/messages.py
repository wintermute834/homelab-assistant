
from typing import Literal, Optional, TypeAlias

from pydantic import BaseModel

from .tool_calls import ToolCall



class SystemMessage(BaseModel):
    role: Literal["system"] = "system"
    content: str


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str
    reasoning_content: Optional[str] = None
    tool_calls: Optional[list[ToolCall]] = None


class ToolResponseMessage(BaseModel):
    role: Literal["tool"] = "tool"
    content: str
    id: str


Message: TypeAlias = SystemMessage | UserMessage | AssistantMessage | ToolResponseMessage
