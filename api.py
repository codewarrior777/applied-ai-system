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
    # NUEVO: Agregamos el campo source a la respuesta de la API
    source: str


@app.post("/api/parse-task", response_model=ParseResponse)
def parse_task_endpoint(request: ParseRequest):
    """
    Endpoint que recibe texto natural y devuelve una tarea estructurada
    usando el Agente de IA (con fallback a Regex).
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="El texto no puede estar vacío.")

    try:
        # 👇 AQUÍ ESTÁ EL CAMBIO: Desempaquetamos la tupla
        parsed, source = parse_task_with_llm(request.text, request.known_pets)
        
        # Convertimos a diccionario, le inyectamos el source, y lo devolvemos
        response_data = parsed.to_dict()
        response_data["source"] = source
        
        return ParseResponse(**response_data)
        
    except ValueError as e:
        # Atrapamos errores específicos de parseo (validación de datos)
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        # Atrapamos cualquier otro error inesperado (ej. caída de red)
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "PawPal+ AI"}