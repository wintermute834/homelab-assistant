"""
Pydantic models for tool definitions that are given to the model.
"""

from typing import Callable, Literal, Optional

from pydantic import BaseModel

from .json import JSON



type Parameter = Object | Array | Primitive


class Object(BaseModel):
    type: Literal["object"] = "object"
    description: Optional[str] = None
    properties: dict[str, Parameter]
    required: Optional[list[str]] = None


class Array(BaseModel):
    type: Literal["array"] = "array"
    description: Optional[str] = None
    items: Parameter


class Primitive(BaseModel):
    type: Literal["string", "number", "boolean", "null"]
    description: Optional[str] = None


class Function(BaseModel):
    name: str
    description: str
    parameters: Optional[Object] = None


class ToolDefinition(BaseModel):
    type: Literal["function"] = "function"
    function: Function


class Tool(BaseModel):
    definition: ToolDefinition
    function: Callable[[*tuple[JSON, ...]], JSON]
