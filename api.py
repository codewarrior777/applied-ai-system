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

@app.post("/api/parse-task", response_model=ParseResponse)
def parse_task_endpoint(request: ParseRequest):
    """
    Endpoint que recibe texto natural y devuelve una tarea estructurada
    usando el Agente de IA (con fallback a Regex).
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")
    
    try:
        # Aquí llamamos al AGENTE (no al parser directo)
        parsed = parse_task_with_llm(request.text, request.known_pets)
        return ParseResponse(**parsed.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PawPal+ AI"}