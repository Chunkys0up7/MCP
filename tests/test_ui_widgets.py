from unittest.mock import MagicMock, patch

import pytest

from mcp.core.types import MCPType
from mcp.ui.widgets.llm_config import build_llm_config
from mcp.ui.widgets.notebook_config import build_notebook_config
from mcp.ui.widgets.script_config import build_script_config


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit functions."""
    with patch("streamlit.selectbox") as mock_selectbox, patch(
        "streamlit.text_area"
    ) as mock_text_area, patch("streamlit.slider") as mock_slider, patch(
        "streamlit.number_input"
    ) as mock_number_input, patch(
        "streamlit.radio"
    ) as mock_radio, patch(
        "streamlit.checkbox"
    ) as mock_checkbox, patch(
        "streamlit.button"
    ) as mock_button, patch(
        "streamlit.success"
    ) as mock_success, patch(
        "streamlit.error"
    ) as mock_error:

        # Configure mock return values
        mock_selectbox.return_value = "claude-3-sonnet-20240229"
        mock_text_area.return_value = "Test template"
        mock_slider.return_value = 0.7
        mock_number_input.return_value = 1000
        mock_radio.return_value = "Use Existing File"
        mock_checkbox.return_value = True
        mock_button.return_value = False

        yield {
            "selectbox": mock_selectbox,
            "text_area": mock_text_area,
            "slider": mock_slider,
            "number_input": mock_number_input,
            "radio": mock_radio,
            "checkbox": mock_checkbox,
            "button": mock_button,
            "success": mock_success,
            "error": mock_error,
        }


def test_build_llm_config(mock_streamlit):
    """Test LLM configuration widget."""
    config = build_llm_config()

    # Verify widget calls
    mock_streamlit["selectbox"].assert_called_once()
    mock_streamlit["text_area"].assert_called()
    mock_streamlit["slider"].assert_called_once()
    mock_streamlit["number_input"].assert_called_once()

    # Verify config values
    assert config.type == MCPType.LLM_PROMPT
    assert config.model_name == "claude-3-sonnet-20240229"
    assert config.template == "Test template"
    assert config.temperature == 0.7
    assert config.max_tokens == 1000


def test_build_notebook_config(mock_streamlit):
    """Test Notebook configuration widget."""
    config = build_notebook_config()

    # Verify widget calls
    mock_streamlit["radio"].assert_called_once()
    mock_streamlit["text_area"].assert_called()
    mock_streamlit["checkbox"].assert_called_once()
    mock_streamlit["number_input"].assert_called_once()

    # Verify config values
    assert config.type == MCPType.JUPYTER_NOTEBOOK
    assert config.execute_all is True
    assert config.timeout == 600


def test_build_script_config(mock_streamlit):
    """Test Script configuration widget."""
    config = build_script_config()

    # Verify widget calls
    mock_streamlit["radio"].assert_called_once()
    mock_streamlit["text_area"].assert_called()
    mock_streamlit["checkbox"].assert_called_once()
    mock_streamlit["number_input"].assert_called_once()

    # Verify config values
    assert config.type == MCPType.PYTHON_SCRIPT
    assert config.virtual_env is True
    assert config.timeout == 300


def test_notebook_save_button(mock_streamlit):
    """Test notebook save button functionality."""
    # Mock button click
    mock_streamlit["button"].return_value = True

    # Mock file operations
    with patch("builtins.open", MagicMock()) as mock_open, patch(
        "json.dump"
    ) as mock_json_dump, patch("os.makedirs") as mock_makedirs, patch(
        "os.path.exists", return_value=False
    ) as mock_exists:

        build_notebook_config()

        # Verify file operations
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()
        mock_streamlit["success"].assert_called_once()


def test_script_save_button(mock_streamlit):
    """Test script save button functionality."""
    # Mock button click
    mock_streamlit["button"].return_value = True

    # Mock file operations
    with patch("builtins.open", MagicMock()) as mock_open, patch(
        "os.makedirs"
    ) as mock_makedirs:

        build_script_config()

        # Verify file operations
        mock_makedirs.assert_called_once()
        mock_open.assert_called_once()
        mock_streamlit["success"].assert_called_once()


def test_error_handling(mock_streamlit):
    """Test error handling in widgets."""
    # Mock file operations to raise exception
    with patch("builtins.open", MagicMock(side_effect=Exception("Test error"))):
        build_script_config()
        mock_streamlit["error"].assert_called_once()
