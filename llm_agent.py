"""
LLM Agent for parsing natural language tasks in PawPal+.
Uses OpenRouter (via the OpenAI SDK) to extract structured JSON.
Includes a Regex fallback for maximum reliability.
"""

import os
import json
import re
from openai import OpenAI
from nl_parser import parse_task as regex_parse_task, ParsedTask
from dotenv import load_dotenv

# Aseguramos que las variables de entorno (.env) se carguen
load_dotenv()

# Configuración del cliente OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "dummy_key")
)

# Modelo exacto obtenido de OpenRouter (Uptime 13.19%)
MODEL = "recursive/flint-v1.0:free"

def parse_task_with_llm(text: str, known_pets: list[str]) -> ParsedTask:
    """Agente de IA con Guardrails y Fallback."""
    
    # Guardrail 0: Verificar si existe la API Key
    if not os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY") == "dummy_key":
        print("[Guardrail] Clave API no encontrada. Usando parser Regex.")
        return regex_parse_task(text, known_pets)

    system_prompt = f"""
    You are an AI assistant for a pet care app. Extract task details from the user's text.
    Return ONLY a valid JSON object with these exact keys:
    - "description": (string) What the task is. Keep the pet's name in it.
    - "time": (string) 24-hour format "HH:MM" (e.g., "07:00", "18:30").
    - "frequency": (string) "once", "daily", or "weekly".
    - "priority": (string) "high", "medium", or "low".
    - "pet_name": (string or null) One of these exact names: {known_pets}.
    
    If you cannot find a time, default to "12:00". If you cannot find a priority, default to "medium".
    Do not include markdown formatting like ```json.
    """

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=150
        )
        
        raw_json = response.choices[0].message.content.strip()
        
        # Guardrail 1: Limpiar markdown si el LLM lo incluye por error
        if raw_json.startswith("```json"):
            raw_json = raw_json.replace("```json", "").replace("```", "").strip()
            
        data = json.loads(raw_json)
        
        # Guardrail 2: Validar formato de hora estricto con Regex (evita alucinaciones como 25:00)
        if not re.match(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$", data.get("time", "")):
             raise ValueError(f"Hora inválida generada por la IA: {data.get('time')}")
             
        # Guardrail 3: Validar que la mascota exista en la base de datos del usuario
        if data.get("pet_name") not in known_pets:
            data["pet_name"] = None
            
        print("[Agentic AI] Tarea extraída por el LLM exitosamente.")
        return ParsedTask(
            description=data.get("description", "Task"),
            time=data.get("time", "12:00"),
            frequency=data.get("frequency", "once"),
            priority=data.get("priority", "medium"),
            pet_name=data.get("pet_name")
        )

    except Exception as e:
        # El Fallback: Si la API falla (404, 429, timeout, etc.), usa Regex y no rompe la app.
        print(f"[Guardrail] Error en LLM ({e}). Usando parser Regex (Fallback).")
        return regex_parse_task(text, known_pets)