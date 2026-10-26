import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from rag.models import DocumentChunk
from rag.retriever import get_model

User = get_user_model()
PASSWORD = "Str0ng#TestPass"


def make_client(username):
    user = User.objects.create_user(username=username, password=PASSWORD)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def new_conversation(client):
    return client.post("/api/conversations/", {"title": "t"}, format="json").data["id"]


def ask(client, conversation_id, text):
    return client.post(
        f"/api/conversations/{conversation_id}/messages/",
        {"content": text},
        format="json",
    )


@pytest.mark.django_db
def test_register_does_not_return_password():
    response = APIClient().post(
        "/api/auth/register/",
        {"username": "newuser", "email": "a@b.com", "password": PASSWORD},
        format="json",
    )
    assert response.status_code == 201
    assert "password" not in response.data


@pytest.mark.django_db
def test_login_returns_tokens():
    User.objects.create_user(username="loginuser", password=PASSWORD)
    response = APIClient().post(
        "/api/auth/login/",
        {"username": "loginuser", "password": PASSWORD},
        format="json",
    )
    assert response.status_code == 200
    assert "access" in response.data and "refresh" in response.data


@pytest.mark.django_db
def test_conversations_require_login():
    assert APIClient().get("/api/conversations/").status_code == 401


@pytest.mark.django_db
def test_user_cannot_read_another_users_conversation():
    owner = make_client("owner")
    other = make_client("other")
    conversation_id = new_conversation(owner)
    response = other.get(f"/api/conversations/{conversation_id}/messages/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_emergency_question_gets_emergency_message():
    client = make_client("u1")
    response = ask(client, new_conversation(client), "I have chest pain")
    reply = response.data["assistant_message"]
    assert "emergency" in reply["content"].lower()
    assert reply["sources"] == []


@pytest.mark.django_db
def test_diagnosis_request_is_refused():
    client = make_client("u2")
    response = ask(client, new_conversation(client), "Do I have diabetes?")
    reply = response.data["assistant_message"]
    assert "can't diagnose" in reply["content"]
    assert reply["sources"] == []


@pytest.mark.django_db
def test_question_with_no_matching_source_gets_fallback():
    client = make_client("u3")
    response = ask(client, new_conversation(client), "Who won the cricket world cup?")
    reply = response.data["assistant_message"]
    assert "couldn't find" in reply["content"]
    assert reply["sources"] == []


@pytest.mark.django_db
def test_answer_contains_sources(monkeypatch):
    monkeypatch.setenv("LLM_MODE", "retrieval_only")
    monkeypatch.setenv("MAX_DISTANCE", "0.6")
    text = (
        "Dengue is a viral infection spread by mosquitoes. Symptoms include high "
        "fever, headache, body aches, nausea and rash."
    )
    embedding = get_model().encode(text, normalize_embeddings=True).tolist()
    DocumentChunk.objects.create(
        source="who_dengue.txt", page=1, chunk_index=0, text=text, embedding=embedding
    )

    client = make_client("u4")
    response = ask(client, new_conversation(client), "What are the symptoms of dengue?")
    reply = response.data["assistant_message"]
    assert reply["sources"][0]["source"] == "who_dengue.txt"