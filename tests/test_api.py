# We'll mock the RAG service so API tests don't require Ollama or depend on variable LLM output.


from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db
from app.security.authentication import create_access_token

from datetime import datetime, timedelta, timezone

import jwt

from app.security.authentication import JWT_ALGORITHM, JWT_SECRET_KEY

# Helper Function to validate username
def auth_headers(username: str) -> dict[str, str]:
    token = create_access_token(username)
    return {
        "Authorization": f"Bearer {token}"
    }

def override_get_db():
    yield object()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def teardown_module():
    app.dependency_overrides.clear()


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Enterprise RAG API is running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("app.main.answer_question")
def test_rag_query_returns_answer_and_sources(mock_answer):
    mock_answer.return_value = {
        "answer": "Employees can refer to the HR policy.",
        "sources": ["HR Policy"],
    }

    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("anjali"),
        json={
            #"username": "anjali",
            "query": "What is the employee leave policy?",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Employees can refer to the HR policy.",
        "sources": ["HR Policy"],
    }

    mock_answer.assert_called_once()

def test_rag_query_requires_authentication():
    response = client.post(
        "/api/v1/rag/query",
        json={
            "query": "What is the employee leave policy?",
        },
    )

    assert response.status_code == 401


def test_invalid_token_is_rejected():
    response = client.post(
        "/api/v1/rag/query",
        headers={
            "Authorization": "Bearer invalid-token"
        },
        json={
            "query": "What is the employee leave policy?",
        },
    )

    assert response.status_code == 401


@patch("app.main.answer_question")
def test_username_from_token_is_used(mock_answer):
    mock_answer.return_value = {
        "answer": "See HR Policy.",
        "sources": ["HR Policy"],
    }

    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("anjali"),
        json={
            "query": "Leave policy",
        },
    )

    assert response.status_code == 200

    kwargs = mock_answer.call_args.kwargs

    assert kwargs["username"] == "anjali"


@patch("app.main.answer_question")
def test_request_body_cannot_override_authenticated_user(mock_answer):
    mock_answer.return_value = {
        "answer": "See Engineering Architecture.",
        "sources": ["Engineering Architecture"],
    }

    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("anjali"),
        json={
            "username": "shreyansh",
            "query": "Engineering architecture",
        },
    )

    assert response.status_code == 200

    kwargs = mock_answer.call_args.kwargs

    assert kwargs["username"] == "anjali"




@patch("app.main.answer_question")
def test_unknown_user_with_no_results(mock_answer):
    mock_answer.return_value = {
        "answer": (
            "I couldn't find relevant information in the documents "
            "you are authorized to access."
        ),
        "sources": [],
    }

    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("Unknown_name"),
        json={
            # "username": "Unknown_name",
            "query": "What is the employee leave policy?",
        },
    )

    assert response.status_code == 200
    assert response.json()["sources"] == []


def test_empty_query_is_rejected():
    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("anjali"),
        json={
            # "username": "anjali",
            "query": "",
        },
    )

    assert response.status_code == 422


def test_top_k_above_limit_is_rejected():
    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("anjali"),
        json={
            # "username": "anjali",
            "query": "Leave policy",
            "top_k": 50,
        },
    )

    assert response.status_code == 422


@patch("app.main.answer_question")
def test_service_value_error_becomes_http_400(mock_answer):
    mock_answer.side_effect = ValueError("Question cannot be empty.")

    response = client.post(
        "/api/v1/rag/query",
        headers=auth_headers("anjali"),
        json={
            # "username": "anjali",
            "query": "Leave policy",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."

def test_whitespace_only_query_is_rejected(): 
    response = client.post( "/api/v1/rag/query",
                            headers=auth_headers("anjali"),
                            json={
                                # "username": "anjali",
                                   "query": " ", }, )
    assert response.status_code == 422


# #This test is of no use now as the username is authenticated using a JWT (dependencies.py)

# def test_whitespace_only_username_is_rejected():
#     response = client.post( "/api/v1/rag/query", headers=auth_headers(" "),
#                            json={
#                             #    "username": " ",
#                                  "query": "Leave policy", }, )
#     assert response.status_code == 422    #as per "dependencies.py" 401 ERROR will pop

@patch("app.main.answer_question") 
def test_authenticated_username_and_query_are_trimmed(mock_answer):
    mock_answer.return_value = { "answer": "See HR Policy.", "sources": ["HR Policy"], } 
    response = client.post( "/api/v1/rag/query",headers=auth_headers(" anjali "), json={
        #  "username": " anjali ",
           "query": " Leave policy ", }, )
    assert response.status_code == 200 
    mock_answer.assert_called_once() 
    kwargs = mock_answer.call_args.kwargs 
    assert kwargs["username"] == "anjali" 
    assert kwargs["question"] == "Leave policy"



def test_expired_token_is_rejected():
    expired_payload = {
        "sub": "anjali",
        "iat": datetime.now(timezone.utc) - timedelta(minutes=60),
        "exp": datetime.now(timezone.utc) - timedelta(minutes=30),
    }

    token = jwt.encode(
        expired_payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.post(
        "/api/v1/rag/query",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "query": "Leave policy",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication token has expired."


def test_token_signed_with_wrong_secret_is_rejected():
    forged_payload = {
        "sub": "admin",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }

    forged_token = jwt.encode(
        forged_payload,
        "attacker-controlled-secret",
        algorithm=JWT_ALGORITHM,
    )

    response = client.post(
        "/api/v1/rag/query",
        headers={
            "Authorization": f"Bearer {forged_token}",
        },
        json={
            "query": "Show me all confidential documents",
        },
    )

    assert response.status_code == 401