# Enterprise RAG with RBAC

A secure internal enterprise knowledge assistant built using Retrieval-Augmented
Generation (RAG), Role-Based Access Control (RBAC), hybrid search, and
prompt-injection defenses.

## Architecture

User
↓
FastAPI
↓
Authentication
↓
RBAC Authorization
↓
Hybrid Retrieval
├── Vector Search
└── Keyword Search
↓
Security / Prompt Injection Guardrails
↓
LLM
↓
Secure Answer

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- pgvector
- SQLAlchemy
- LangChain
- Ollama
- JWT Authentication
- Pytest

## Data Sources

The planned system will support:

- PDF documents
- PostgreSQL / SQL data
- Confluence pages

## Security

The system is designed so that authorization is applied before protected
content is passed to the language model.

Planned security capabilities include:

- JWT authentication
- Role-Based Access Control
- Document-level permissions
- Prompt-injection detection
- Retrieval filtering
- Audit logging

## Current Status

Day 1 - Project and infrastructure setup completed.