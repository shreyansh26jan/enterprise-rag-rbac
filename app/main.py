from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import RAGQueryRequest, RAGQueryResponse
from app.db.database import get_db
from app.generation.rag_service import answer_question
from app.security.dependencies import get_current_username


app = FastAPI(
    title="Enterprise RAG with RBAC",
    description="Secure internal knowledge assistant",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Enterprise RAG API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.post("/api/v1/rag/query", response_model=RAGQueryResponse)
def rag_query( request: RAGQueryRequest, db: Session = Depends(get_db), username: str = Depends(get_current_username), ):
    try:
        result = answer_question( db=db, username= username, question=request.query, top_k=request.top_k, ) #username = request.username.strip()
        return result
    except ValueError as exc:
        raise HTTPException( status_code=400, detail=str(exc), ) from exc