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

## Day 4 : Hybrid Search and Access Control

The system supports hybrid retrieval by combining semantic vector search with keyword-based search. Results from both retrieval methods are merged, deduplicated by chunk ID, and ranked using a weighted scoring strategy.

### Retrieval Pipeline

1. Validate the user's query and requested result count.
2. Retrieve semantically similar chunks using vector search.
3. Retrieve matching chunks using keyword search.
4. Enforce role-based document access within each retrieval query.
5. Merge and deduplicate results.
6. Rank results using a weighted combination of vector similarity and keyword rank.

### Security Features

* Active-user validation
* Role-based document access
* Authorization filtering in both vector and keyword retrieval
* Empty-query and invalid-result-count validation
* Tests for unauthorized access and unknown users

### Example Demonstration

The hybrid-search demonstration verifies three user scenarios:

* **Anjali:** Can retrieve HR Policy and public company information, but not Engineering Architecture.
* **Shreyansh:** Can retrieve Engineering Architecture and public company information, but not HR Policy.
* **Raj:** Can retrieve public company information only.

### Testing

Run the complete test suite:

```powershell
python -m pytest -q
```

The current test suite passes all 37 tests.

### Current Limitations

* Keyword retrieval currently uses substring matching with PostgreSQL `ILIKE`.
* Hybrid ranking uses a heuristic weighted score; the scores have not been calibrated against a relevance evaluation dataset.
* PDF and Confluence ingestion, production identity integration, and the final answer-generation pipeline remain separate development tasks.



## Day 5: RAG Generation Pipeline

Implemented the initial Retrieval-Augmented Generation (RAG) pipeline to generate answers from documents retrieved according to user permissions.

### Features Implemented

* **Context Builder:** Converts retrieved document chunks into a structured context containing source document names and content.
* **Prompt Construction:** Builds prompts using the user's question and retrieved context, with instructions to answer using the available information and avoid unsupported claims.
* **LLM Integration:** Integrated a locally hosted language model using Ollama and LangChain's `ChatOllama` interface.
* **Configurable Model:** Configured the LLM model through the `LLM_MODEL` environment variable.
* **RAG Service:** Implemented an end-to-end service that combines hybrid retrieval, context construction, prompt generation, and LLM-based answer generation.
* **Source Metadata:** Returns source document names separately from the generated answer.
* **Access-Controlled Retrieval:** Ensures that the generation pipeline receives results from the existing RBAC-aware hybrid search.
* **Empty-Query Validation:** Rejects empty or whitespace-only questions.
* **No-Results Handling:** Returns a fallback response without invoking the LLM when no relevant authorized documents are retrieved.

### Testing

* Added unit tests for context construction, prompt generation, LLM configuration, and RAG service validation.
* Added integration tests covering authorized HR retrieval, exclusion of unauthorized HR content for engineering users, and handling of unknown users.
* Verified that the existing authorization, vector search, keyword search, and hybrid search tests continue to pass.

**Test Result:** 55 tests passed.

### Current Limitations

* Hybrid-search relevance tuning and score-threshold optimization are deferred to a later stage.
* The sample HR document describes leave policies but does not specify actual leave entitlements or procedures. The assistant must not invent those details.
* Prompt-based defenses against prompt injection are preliminary and are not a complete security boundary.
* The current pipeline uses a local Ollama model; answer quality and generation behavior require further evaluation.



## Day 6: FastAPI RAG API

The project exposes a REST API for querying internal company knowledge through a Retrieval-Augmented Generation (RAG) pipeline.

### Start the API

Activate the virtual environment and run:

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

Interactive API documentation: `http://127.0.0.1:8000/docs`

### Endpoints

| Method | Endpoint            | Description         |
| ------ | ------------------- | ------------------- |
| GET    | `/`                 | API welcome message |
| GET    | `/health`           | Health check        |
| POST   | `/api/v1/rag/query` | Submit a RAG query  |

### Example request

```json
{
  "username": "anjali",
  "query": "What is the employee leave policy?",
  "top_k": 3
}
```

### Example response

```json
{
  "answer": "See the relevant HR documentation.",
  "sources": [
    "HR Policy"
  ]
}
```

The answer and sources above are illustrative; actual results depend on retrieved documents and the configured language model.

### Security

* Queries use the existing RBAC-aware hybrid retrieval pipeline.
* Document authorization is applied before retrieved content reaches the generation stage.
* Unknown users receive no document results under the current authorization implementation.
* Request validation rejects empty or whitespace-only usernames and queries.
* `top_k` is restricted to the range 1–10.

**Authentication note:** The current API accepts a username in the request body. This is suitable for development and testing, but it does not authenticate the caller. Production deployment requires verified identity, server-side user resolution, and appropriate authentication and authorization controls.


## Day 7: Authentication & Trusted Identity

The API uses JSON Web Tokens (JWT) with HTTP Bearer authentication to establish a trusted user identity before processing RAG queries.

### Authentication Flow

1. The client sends a request with a JWT in the `Authorization` header.
2. The authentication dependency validates the token signature and expiration.
3. The authenticated username is extracted from the token's `sub` claim.
4. The trusted username is passed to the RAG service.
5. The existing Role-Based Access Control (RBAC) layer restricts retrieval to documents the user is authorized to access.
6. The LLM generates an answer using the authorized retrieval results.

**Security principle:** The API does not rely on a username supplied in the RAG request body. User identity is derived from the validated JWT, preventing clients from selecting another user's identity through request data.

### API Authentication

Endpoint:

`POST /api/v1/rag/query`

Authentication header:

```http
Authorization: Bearer <access_token>
```

Example request body:

```json
{
  "query": "What is the employee leave policy?",
  "top_k": 3
}
```

The request body contains the query and retrieval limit; it does not contain a username.

### Token Configuration

Configure the following environment variables:

| Variable                 | Description                                  |
| ------------------------ | -------------------------------------------- |
| `JWT_SECRET_KEY`         | Secret used to sign and verify JWTs          |
| `JWT_ALGORITHM`          | JWT signing algorithm, configured as `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes                    |

Keep the JWT secret in the local `.env` file. Never commit secrets to version control. The `.env.example` file should contain placeholder values only.

For local development, the application provides a token-generation utility. In a production deployment, tokens should normally be issued by a trusted identity provider, such as Microsoft Entra ID, Okta, or Keycloak.

### Authentication Error Handling

| Scenario                           |                HTTP status |
| ---------------------------------- | -------------------------: |
| Missing authentication credentials |         `401 Unauthorized` |
| Invalid token                      |         `401 Unauthorized` |
| Expired token                      |         `401 Unauthorized` |
| Invalid request data               | `422 Unprocessable Entity` |

### Security Testing

The automated test suite verifies:

* Requests without authentication are rejected.
* Invalid, expired, and incorrectly signed JWTs are rejected.
* The username extracted from a valid token is used by the RAG service.
* A username supplied in the request body cannot override the authenticated identity.
* Existing RBAC, authorized retrieval, hybrid search, and RAG functionality remain intact.

### Security Architecture

```text
Client Request
      |
      v
JWT Authentication
(app/security/)
      |
      v
Trusted User Identity
      |
      v
RBAC Authorization
(app/auth/)
      |
      v
Authorized Document Retrieval
(app/retrieval/)
      |
      v
RAG Generation
(app/generation/)
      |
      v
Answer + Sources
```

Authentication establishes **who the user is**; RBAC determines **which information the user may access**. Both layers are required for secure enterprise knowledge retrieval.



## Day 8: Prompt-Injection Defenses and Authentication

The RAG pipeline applies defense-in-depth measures to reduce prompt-injection risks.

### Implemented safeguards

* **Explicit trust boundaries:** The system prompt identifies retrieved document content as untrusted data.
* **Instruction isolation:** The LLM is instructed not to follow commands embedded in retrieved documents or allow them to override system instructions.
* **RBAC enforcement:** Document retrieval remains subject to the existing authorization layer. A user query cannot grant additional permissions.
* **Regression testing:** Tests cover malicious document content, attempted authorization manipulation, and prompt construction through the RAG service.
* **Isolated adversarial fixture:** `data/test_documents/prompt_injection.txt` contains intentionally malicious test content and is kept separate from the normal sample dataset.

### Security limitations

Prompt instructions alone cannot guarantee immunity to prompt injection. These measures reduce risk but do not replace authorization enforcement, output validation, or additional adversarial evaluation.

The adversarial fixture is not part of the normal ingestion dataset unless explicitly ingested by a test or development workflow.

### JWT-Based Authentication

The API uses JSON Web Tokens (JWT) to authenticate requests to protected endpoints.

* **Bearer token authentication:** Protected endpoints require a valid JWT in the `Authorization` header.
* **Signature validation:** Tokens are verified using the configured signing algorithm and secret key.
* **Required claims:** Tokens must contain `sub` (subject), `iat` (issued at), and `exp` (expiration).
* **Expiration validation:** Expired tokens are rejected.
* **Subject validation:** Missing, invalid, or blank usernames are rejected.
* **Identity integrity:** The authenticated username is extracted from the validated token rather than trusted from the request body.
* **Error handling:** Missing credentials, invalid tokens, expired tokens, and invalid claims produce HTTP 401 responses.

### Role-Based Access Control (RBAC)

Authentication and authorization are separate responsibilities:

* **Authentication** verifies the user's identity through the JWT.
* **Authorization** determines which documents the authenticated user may access.
* Document retrieval applies authorization restrictions before retrieved content is passed to the generation layer.
* Users without permitted documents must not receive restricted document content.
* A valid token alone does not grant access to every document.

### Prompt-Injection Defenses

Retrieved documents and user questions are treated as untrusted input.

* The RAG system prompt establishes explicit security and grounding rules.
* Instructions embedded in retrieved documents must be treated as document content, not as system or developer instructions.
* Retrieved content cannot grant permissions, change the authenticated user's identity, or override RBAC.
* Answers should use retrieved context only and avoid inventing unsupported information.
* The assistant should indicate when available documents do not contain sufficient information to answer a question.
* Source document names are included in generated answers where applicable.
* Malicious prompt-injection content is included in isolated test documents to validate defensive behavior.

**Security note:** Prompt instructions are a defense-in-depth measure, not a complete guarantee against prompt injection. Authorization must be enforced independently in the retrieval and data-access layers.

### Security Test Coverage

Automated tests cover:

* Missing authentication credentials and invalid tokens.
* Expired tokens and tokens signed with an incorrect secret.
* Tokens missing required claims or containing invalid subjects.
* Preventing request-body fields from overriding the authenticated identity.
* Input validation and API error handling.
* Role-based document access and restrictions.
* Prompt-injection handling and preservation of retrieval authorization boundaries.


## Day 9: PDF Document Ingestion

The project supports ingestion of PDF documents alongside the existing text-based ingestion workflow.

**Features**
- Extracts text from PDFs using `pypdf`.
- Splits extracted text using the shared chunking utility.
- Stores chunks with document IDs, chunk indices, and page numbers.
- Generates vector embeddings using the existing embedding pipeline.
- Uses the existing document-level role-based access controls during retrieval.
- Supports re-ingestion by replacing the document's previous chunks.

**Workflow**

1. Register the document in the database and assign its classification and authorized roles.
2. Configure the document name and PDF path in `app/ingestion/run_pdf_ingestion.py`.
3. Run `python -m app.ingestion.run_pdf_ingestion`.
4. Generate embeddings for chunks that do not yet have embeddings with `python -m app.ingestion.embed_chunks`.

**Testing**

Run `pytest -q` to execute the test suite, including PDF extraction, page-number storage, re-ingestion, validation, and retrieval-related regression tests.
