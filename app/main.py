from fastapi import FastAPI

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