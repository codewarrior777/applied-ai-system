import os
from unittest.mock import MagicMock, patch

from llm_agent import parse_task_with_llm
from nl_parser import ParsedTask, parse_task

# --- TESTS PARA EL REGEX FALLBACK (nl_parser.py) ---


def test_regex_parser_defaults_to_12_00_when_no_time():
    """Verify that the regex parser defaults to 12:00 if no time is found."""
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

# Usamos @patch.dict para forzar que la API KEY exista durante el test
# y así evitar que la Guardrail 0 se dispare y oculte el verdadero test.
@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_fallback_when_api_fails(mock_create):
    """Verify that if the API fails, it falls back to the regex parser."""
    # Simulamos un error de la API (ej. timeout o 500 error)
    mock_create.side_effect = Exception("API Connection Error")

    result = parse_task_with_llm("Feed Prince at 12:00", ["Prince"])

    # Debería usar el fallback de regex y no romperse
    assert isinstance(result, ParsedTask)
    assert result.time == "12:00"
    # Verificamos que el mock SÍ fue llamado (el test es real)
    mock_create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_cleans_markdown(mock_create):
    """Verify Guardrail 1: The agent strips markdown code blocks from the LLM response."""
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '```json\n{"description": "Walk Cooper", "time": "07:00", "frequency": "daily", "priority": "high", "pet_name": "Cooper"}\n```'
    mock_create.return_value = mock_response

    result = parse_task_with_llm("Walk Cooper at 7am daily", ["Cooper"])
    assert result.time == "07:00"
    mock_create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_guardrail_invalid_time(mock_create):
    """Verify Guardrail 2: The agent defaults to 12:00 if the LLM hallucinates an invalid time."""
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"description": "Feed Prince", "time": "25:00", "frequency": "once", "priority": "medium", "pet_name": "Prince"}'
    mock_create.return_value = mock_response

    result = parse_task_with_llm("Feed Prince at 25:00", ["Prince"])
    assert result.time == "12:00"
    mock_create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_guardrail_unknown_pet(mock_create):
    """Verify Guardrail 3: The agent sets pet_name to None if the pet is not in the known list."""
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"description": "Feed unknown", "time": "12:00", "frequency": "once", "priority": "medium", "pet_name": "UnknownPet"}'
    mock_create.return_value = mock_response

    result = parse_task_with_llm("Feed UnknownPet", ["Prince", "Cooper"])
    assert result.pet_name is None
    mock_create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.client.chat.completions.create")
def test_llm_agent_guardrail_invalid_frequency_and_priority(mock_create):
    """Verify Guardrail 4: The agent corrects invalid frequency and priority values."""
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"description": "Walk Cooper", "time": "10:00", "frequency": "every hour", "priority": "urgent", "pet_name": "Cooper"}'
    mock_create.return_value = mock_response

    result = parse_task_with_llm("Walk Cooper every hour", ["Cooper"])
    assert result.frequency == "once"
    assert result.priority == "medium"
    mock_create.assert_called_once()