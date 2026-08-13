
from typing import Optional

from pydantic import BaseModel

from .messages import Message
from .tool_defs import ToolDefinition



class Query(BaseModel):
    model: str
    tools: Optional[list[ToolDefinition]] = None
    messages: list[Message]
