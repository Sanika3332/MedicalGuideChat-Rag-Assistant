import os

from .generator import generate_answer
from .guardrails import (
    DIAGNOSIS_MESSAGE,
    DISCLAIMER,
    EMERGENCY_MESSAGE,
    NO_INFO_MESSAGE,
    asks_for_diagnosis,
    is_emergency,
)
from .retriever import retrieve


def answer_question(question):
    if is_emergency(question):
        return EMERGENCY_MESSAGE, []
    if asks_for_diagnosis(question):
        return DIAGNOSIS_MESSAGE, []

    max_distance = float(os.getenv("MAX_DISTANCE", "0.6"))
    chunks = [c for c in retrieve(question) if c["distance"] <= max_distance]
    if not chunks:
        return NO_INFO_MESSAGE, []

    if os.getenv("LLM_MODE", "live") == "retrieval_only":
        answer = f"(Retrieval-only mode, no LLM) Most relevant passage:\n{chunks[0]['text']}"
    else:
        answer = generate_answer(question, chunks)

    sources = [
        {"source": c["source"], "page": c["page"], "chunk_index": c["chunk_index"]}
        for c in chunks
    ]
    return answer + DISCLAIMER, sources