from pydantic import BaseModel, Field, field_validator


class RAGQueryRequest(BaseModel):
    username: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)

    """min_length=1 rejects empty strings but allows whitespace-only usernames and queries.
      Let's close that gap. The function below ensures that: 
      1. "   " is rejected for both username and query.
      2. Leading and trailing whitespace is removed.
      3. top_k remains restricted to 1–10."""

    @field_validator("username", "query") 
    @classmethod 
    def reject_blank_strings(cls, value: str) -> str: 
        value = value.strip() 
        if not value: 
            raise ValueError("This field cannot be empty or whitespace.") 
        return value

# Request JSON:
# {
#     "username": "anjali",
#     "query": "What is the employee leave policy?",
#     "top_k": 3
# }    


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[str]

# Response JSON:
# {
#     "answer": "...",
#     "sources": [
#         {
#             "document": "HR Policy",
#             "score": 0.51
#         }
#     ]
# }