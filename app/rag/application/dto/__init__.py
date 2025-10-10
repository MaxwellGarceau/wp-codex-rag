from pydantic import BaseModel, Field


class RAGQueryRequestDTO(BaseModel):
    question: str = Field(..., description="End-user question about WordPress")


class RAGSourceDTO(BaseModel):
    title: str = Field(..., description="Source title")
    url: str = Field(..., description="Source URL")


class RAGQueryResponseDTO(BaseModel):
    answer: str = Field(..., description="Generated answer")
    sources: list[RAGSourceDTO] = Field(default_factory=list, description="Citations")

