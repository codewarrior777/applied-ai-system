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
@patch("llm_agent.OpenAI")  # <--- CAMBIO AQUÍ: Parcheamos la clase OpenAI
def test_llm_agent_fallback_when_api_fails(mock_openai):
    """Verify that if the API fails, it falls back to the regex parser."""
    # Simulamos un error de la API
    mock_client = MagicMock()
    mock_openai.return_value = mock_client
    mock_client.chat.completions.create.side_effect = Exception("API Connection Error")

    result = parse_task_with_llm("Feed Prince at 12:00", ["Prince"])

    assert isinstance(result, ParsedTask)
    assert result.time == "12:00"
    mock_client.chat.completions.create.assert_called_once()


# ... (El resto de tus tests siguen igual, solo cambia el @patch("llm_agent.OpenAI") y añade el mock_client)
