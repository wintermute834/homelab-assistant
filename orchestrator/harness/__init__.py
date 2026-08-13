"""
A simple llama.cpp LLM harness that allows for custom tools.
"""

from .harness import Harness
from .llama_client import LlamaClient

from .types.json import JSON
from .types.tool_defs import Tool
