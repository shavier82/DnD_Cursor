"""Rules helpers — Milestone 2 will prefer RAG over hard-coded rules."""

def adjudication_needed(reason: str) -> dict:
    return {"adjudication_needed": True, "reason": reason}
