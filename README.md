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


### Day 1 — Project & Infrastructure Setup

* FastAPI project structure created
* Python virtual environment configured
* PostgreSQL 18.6 configured
* pgvector installed and verified
* Database connectivity established
* Initial database and pgvector tests implemented
* Sample enterprise documents added
* Environment configuration and `.gitignore` configured

### Day 2 — RBAC Foundation

* Implemented database-backed Role-Based Access Control (RBAC)
* Added SQLAlchemy models for:

  * Users
  * Roles
  * Permissions
  * Documents
* Implemented many-to-many relationships between:

  * Users ↔ Roles
  * Roles ↔ Permissions
  * Roles ↔ Documents
* Added initial enterprise roles:

  * `admin`
  * `hr_manager`
  * `engineer`
  * `employee`
* Added document permissions and classifications
* Implemented user permission and document authorization checks
* Added automated RBAC authorization tests
* **8/8 tests passing**

### Current Security Flow


User
  ↓
Role
  ↓
Permissions
  ↓
Authorized Documents
  ↓
RAG Retrieval


The next stage will integrate RBAC directly with the retrieval layer so that unauthorized documents are excluded from the retrieval candidate set before they can enter the LLM context.


## Day 3: Ingestion and Vector Retrieval

### Features

* Text ingestion and chunking with configurable chunk size and overlap.
* Embedding generation using Ollama's `mxbai-embed-large` model.
* Storage of 1,024-dimensional embeddings in PostgreSQL using pgvector.
* Cosine-similarity search over document chunks.
* Role-based authorization applied within the retrieval query.
* Automated tests covering document access boundaries and invalid queries.

### Run ingestion

```bash
python -m app.ingestion.run_ingestion
```

### Generate embeddings

Ensure Ollama is running and `mxbai-embed-large` is available.

```bash
python -m app.ingestion.embed_chunks
```

### Run tests

```bash
pytest -v
```

### Current limitations

* Sample documents are plain text; PDF and Confluence ingestion are future extensions.
* Keyword and hybrid search are not implemented yet.
* LLM answer generation and prompt-injection defenses remain future tasks.
* Database schema changes are currently applied manually; migrations should be added as the project matures.
