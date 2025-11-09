from pydantic import BaseModel, Field
from typing import List, Literal, Optional

Role = Literal["system", "user", "assistant"]

class Message(BaseModel):
    role: Role
    content: str = Field(..., min_length=1)

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = False
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    model: str
    provider: str