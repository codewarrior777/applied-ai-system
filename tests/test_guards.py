import pytest
from unittest.mock import patch, MagicMock
from llm_agent import parse_task_with_llm
from nl_parser import parse_task, ParsedTask

# --- TESTS PARA EL REGEX FALLBACK (nl_parser.py) ---

def test_regex_parser_defaults_to_12_00_when_no_time():
    """Verify that the regex parser defaults to 12:00 if no time is found."""
    # Este es el ejemplo del README que fallaba antes
    result = parse_task("Feed Prince", ["Prince"])
    assert result.time == "12:00"
    assert result.description == "Feed Prince"
    assert result.pet_name == "Prince"

def test_regex_parser_extracts_valid_time():
    """Verify that the regex parser correctly extracts a valid time."""
    result = parse_task("Walk Cooper at 7:30pm daily", ["Cooper"])
    assert result.time == "19:30"
    assert result.frequency == "daily"

# --- TESTS PARA EL LLM AGENT Y SUS GUARDS (llm_agent.py) ---

@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_fallback_when_api_fails(mock_create):
    """Verify that if the API fails, it falls back to the regex parser."""
    # Simulamos un error de la API (ej. timeout o 500 error)
    mock_create.side_effect = Exception("API Connection Error")
    
    result = parse_task_with_llm("Feed Prince at 12:00", ["Prince"])
    
    # Debería usar el fallback de regex y no romperse
    assert isinstance(result, ParsedTask)
    assert result.time == "12:00"

@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_cleans_markdown(mock_create):
    """Verify Guardrail 1: The agent strips markdown code blocks from the LLM response."""
    # Simulamos que el LLM devuelve JSON con markdown
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '```json\n{"description": "Walk Cooper", "time": "07:00", "frequency": "daily", "priority": "high", "pet_name": "Cooper"}\n```'
    mock_create.return_value = mock_response
    
    result = parse_task_with_llm("Walk Cooper at 7am daily", ["Cooper"])
    assert result.time == "07:00"

@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_guardrail_invalid_time(mock_create):
    """Verify Guardrail 2: The agent defaults to 12:00 if the LLM hallucinates an invalid time."""
    # Simulamos que el LLM devuelve una hora inválida (25:00)
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"description": "Feed Prince", "time": "25:00", "frequency": "once", "priority": "medium", "pet_name": "Prince"}'
    mock_create.return_value = mock_response
    
    result = parse_task_with_llm("Feed Prince at 25:00", ["Prince"])
    # El guardrail debe corregirlo a 12:00
    assert result.time == "12:00"

@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_guardrail_unknown_pet(mock_create):
    """Verify Guardrail 3: The agent sets pet_name to None if the pet is not in the known list."""
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"description": "Feed unknown", "time": "12:00", "frequency": "once", "priority": "medium", "pet_name": "UnknownPet"}'
    mock_create.return_value = mock_response
    
    result = parse_task_with_llm("Feed UnknownPet", ["Prince", "Cooper"])
    # El guardrail debe anular el nombre de la mascota desconocida
    assert result.pet_name is None