
from typing import Literal, Optional

from pydantic import BaseModel

from .messages import AssistantMessage



class ModelResponse(BaseModel):
    finish_reason: Literal["stop", "length", "tool_calls"]
    message: AssistantMessage


class PrompTokensDetails(BaseModel):
    cached_tokens: int


class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    prompt_tokens_details: PrompTokensDetails


class Timings(BaseModel):
    cache_n: int
    prompt_n: int
    prompt_ms: float
    prompt_per_token_ms: float
    prompt_per_second: float
    predicted_n: int
    predicted_ms: float
    predicted_per_token_ms: float
    predicted_per_second: float
    draft_n: Optional[int] = None
    draft_n_accepted: Optional[int] = None


class ServerResponse(BaseModel):
    choices: list[ModelResponse]
    created: int
    model: str
    system_fingerprint: str
    object: Literal["chat.completion"]
    usage: Usage
    id: str
    timings: Timings

