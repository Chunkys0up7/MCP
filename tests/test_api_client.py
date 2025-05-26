from unittest.mock import AsyncMock, patch

import aiohttp
import pytest

from mcp.api.client import MCPClient
from mcp.core.types import (JupyterNotebookConfig, LLMPromptConfig, MCPType,
                            PythonScriptConfig)


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession."""
    with patch("aiohttp.ClientSession") as mock_session:
        mock_session.return_value.__aenter__.return_value = AsyncMock()
        yield mock_session


@pytest.fixture
def mock_response():
    """Mock aiohttp response."""
    mock = AsyncMock()
    mock.status = 200
    mock.json = AsyncMock(return_value={"result": "test result"})
    return mock


@pytest.mark.asyncio
async def test_llm_prompt_execution(mock_aiohttp_session, mock_response):
    """Test LLM prompt execution."""
    # Setup
    mock_aiohttp_session.return_value.__aenter__.return_value.post.return_value = (
        mock_response
    )
    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
    )

    # Execute
    result = await client.execute_llm_prompt(config, {"text": "prompt"})

    # Verify
    assert result == {"result": "test result"}
    mock_aiohttp_session.return_value.__aenter__.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_notebook_execution(mock_aiohttp_session, mock_response):
    """Test notebook execution."""
    # Setup
    mock_aiohttp_session.return_value.__aenter__.return_value.post.return_value = (
        mock_response
    )
    client = MCPClient()
    config = JupyterNotebookConfig(
        name="Test Notebook",
        type=MCPType.JUPYTER_NOTEBOOK,
        input_variables=["data"],
        notebook_path="test.ipynb",
        execute_all=True,
        timeout=600,
    )

    # Execute
    result = await client.execute_notebook(config, {"data": "test"})

    # Verify
    assert result == {"result": "test result"}
    mock_aiohttp_session.return_value.__aenter__.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_script_execution(mock_aiohttp_session, mock_response):
    """Test script execution."""
    # Setup
    mock_aiohttp_session.return_value.__aenter__.return_value.post.return_value = (
        mock_response
    )
    client = MCPClient()
    config = PythonScriptConfig(
        name="Test Script",
        type=MCPType.PYTHON_SCRIPT,
        input_variables=["input"],
        script_path="test.py",
        requirements=["requests>=2.31.0"],
        virtual_env=True,
        timeout=300,
    )

    # Execute
    result = await client.execute_script(config, {"input": "test"})

    # Verify
    assert result == {"result": "test result"}
    mock_aiohttp_session.return_value.__aenter__.return_value.post.assert_called_once()


@pytest.mark.asyncio
async def test_error_handling(mock_aiohttp_session):
    """Test error handling."""
    # Setup
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.json = AsyncMock(return_value={"error": "Bad request"})
    mock_aiohttp_session.return_value.__aenter__.return_value.post.return_value = (
        mock_response
    )

    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
    )

    # Execute and verify error
    with pytest.raises(Exception) as exc_info:
        await client.execute_llm_prompt(config, {"text": "prompt"})
    assert "Bad request" in str(exc_info.value)


@pytest.mark.asyncio
async def test_timeout_handling(mock_aiohttp_session):
    """Test timeout handling."""
    # Setup
    mock_aiohttp_session.return_value.__aenter__.return_value.post.side_effect = (
        aiohttp.ClientTimeout()
    )

    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
    )

    # Execute and verify timeout error
    with pytest.raises(aiohttp.ClientTimeout):
        await client.execute_llm_prompt(config, {"text": "prompt"})


@pytest.mark.asyncio
async def test_connection_error_handling(mock_aiohttp_session):
    """Test connection error handling."""
    # Setup
    mock_aiohttp_session.return_value.__aenter__.return_value.post.side_effect = (
        aiohttp.ClientError()
    )

    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
    )

    # Execute and verify connection error
    with pytest.raises(aiohttp.ClientError):
        await client.execute_llm_prompt(config, {"text": "prompt"})
