from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=32000)
    session_id: str | None = None


class QueryResponse(BaseModel):
    session_id: str
    reply: str
    used_tools: list[str] = Field(default_factory=list)
    mode: str  # "llm" | "echo"
