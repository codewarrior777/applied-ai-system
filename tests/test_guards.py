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


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.OpenAI")
def test_llm_agent_fallback_when_api_fails(mock_openai):
    """Verify that if the API fails, it falls back to the regex parser."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Connection Error")

    result = parse_task_with_llm("Feed Prince at 12:00", ["Prince"])

    assert isinstance(result, ParsedTask)
    assert result.time == "12:00"
    mock_client.chat.completions.create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.OpenAI")
def test_llm_agent_cleans_markdown(mock_openai):
    """Verify Guardrail 1: The agent strips markdown code blocks from the LLM response."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '```json\n{"description": "Walk Cooper", "time": "07:00", "frequency": "daily", "priority": "high", "pet_name": "Cooper"}\n```'
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_task_with_llm("Walk Cooper at 7am daily", ["Cooper"])
    assert result.time == "07:00"
    mock_client.chat.completions.create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.OpenAI")
def test_llm_agent_guardrail_invalid_time(mock_openai):
    """Verify Guardrail 2: The agent defaults to 12:00 if the LLM hallucinates an invalid time."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"description": "Feed Prince", "time": "25:00", "frequency": "once", "priority": "medium", "pet_name": "Prince"}'
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_task_with_llm("Feed Prince at 25:00", ["Prince"])
    assert result.time == "12:00"
    mock_client.chat.completions.create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.OpenAI")
def test_llm_agent_guardrail_unknown_pet(mock_openai):
    """Verify Guardrail 3: The agent sets pet_name to None if the pet is not in the known list."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"description": "Feed unknown", "time": "12:00", "frequency": "once", "priority": "medium", "pet_name": "UnknownPet"}'
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_task_with_llm("Feed UnknownPet", ["Prince", "Cooper"])
    assert result.pet_name is None
    mock_client.chat.completions.create.assert_called_once()


@patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-12345"}, clear=True)
@patch("llm_agent.OpenAI")
def test_llm_agent_guardrail_invalid_frequency_and_priority(mock_openai):
    """Verify Guardrail 4: The agent corrects invalid frequency and priority values."""
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_response = MagicMock()
    mock_response.choices[
        0
    ].message.content = '{"description": "Walk Cooper", "time": "10:00", "frequency": "every hour", "priority": "urgent", "pet_name": "Cooper"}'
    mock_client.chat.completions.create.return_value = mock_response

    result = parse_task_with_llm("Walk Cooper every hour", ["Cooper"])
    assert result.frequency == "once"
    assert result.priority == "medium"
    mock_client.chat.completions.create.assert_called_once()


@patch.dict(os.environ, {}, clear=True)
def test_llm_agent_guardrail_missing_api_key():
    """Verify Guardrail 0: The agent uses the Regex fallback if the API key is missing."""
    # No necesitamos mockear OpenAI aquí, porque la función debería salir ANTES
    # de crear el cliente.
    result = parse_task_with_llm("Feed Prince at 12:00", ["Prince"])

    # Verificamos que el fallback de regex se usó correctamente
    assert isinstance(result, ParsedTask)
    assert result.time == "12:00"
    assert result.pet_name == "Prince"
