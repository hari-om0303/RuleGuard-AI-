from typing import List, Optional, Literal

try:
    from pydantic import BaseModel, Field
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return {k: getattr(self, k) for k in self.__dict__}

    def Field(default=..., **kwargs):
        return default

class SourcePassage(BaseModel):
    document: str = Field(..., description="Name of the source document")
    section: str = Field(..., description="Section number e.g. Section 4.2")
    title: str = Field(..., description="Section title")
    passage: str = Field(..., description="Relevant text passage excerpt")
    similarity: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    page: Optional[int] = Field(None, description="Page number if applicable")
    source_type: str = Field("markdown", description="Document format type (markdown, pdf, table)")

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question asked by the user")

class QueryResponse(BaseModel):
    status: Literal["answered", "not_covered", "conflict"] = Field(..., description="Categorical response status")
    answer: str = Field(..., description="Grounded response text")
    sources: List[SourcePassage] = Field(default_factory=list, description="Retrieved source passages")
