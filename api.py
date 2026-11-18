from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llm_agent import parse_task_with_llm

app = FastAPI(title="PawPal+ AI API")


class ParseRequest(BaseModel):
    text: str
    known_pets: list[str] = []


class ParseResponse(BaseModel):
    description: str
    time: str
    frequency: str
    priority: str
    pet_name: str | None
    # NEW: Include the source field to track observability
    source: str


@app.post("/api/parse-task", response_model=ParseResponse)
def parse_task_endpoint(request: ParseRequest):
    """
    Endpoint that receives natural language text and returns a structured task
    using the AI Agent (with Regex fallback).
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    try:
        # Unpack the tuple returned by the agent (task, source)
        parsed, source = parse_task_with_llm(request.text, request.known_pets)

        # Convert to dictionary, inject the source, and return
        response_data = parsed.to_dict()
        response_data["source"] = source

        return ParseResponse(**response_data)

    except ValueError as e:
        # Catch specific parsing errors (data validation)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        # Catch any other unexpected errors (e.g., network failure)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PawPal+ AI"}
