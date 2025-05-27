import pytest
import httpx
from httpx import Response, Request, MockTransport

from mcp.api.client import MCPClient
from mcp.core.types import (JupyterNotebookConfig, LLMPromptConfig, MCPType,
                            PythonScriptConfig)
from mcp.api.exceptions import MCPAPIError, MCPValidationError, MCPNotFoundError


@pytest.fixture
def mock_transport():
    """Fixture for httpx.MockTransport."""
    def handler(request: Request):
        # Default: always return 200 with a test result
        return Response(200, json={"result": "test result"})
    return MockTransport(handler)


@pytest.mark.asyncio
async def test_llm_prompt_execution(mock_transport):
    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
        id="llm-1"
    )
    # Patch httpx.AsyncClient to use mock_transport
    async with httpx.AsyncClient(transport=mock_transport) as ac:
        # Patch MCPClient to use this client
        client._async_client = ac
        result = await client.execute_llm_prompt(config, {"text": "prompt"})
        assert result == {"result": "test result"}


@pytest.mark.asyncio
async def test_notebook_execution(mock_transport):
    client = MCPClient()
    config = JupyterNotebookConfig(
        name="Test Notebook",
        type=MCPType.JUPYTER_NOTEBOOK,
        input_variables=["data"],
        notebook_path="test.ipynb",
        execute_all=True,
        timeout=600,
        id="notebook-1"
    )
    async with httpx.AsyncClient(transport=mock_transport) as ac:
        client._async_client = ac
        result = await client.execute_notebook(config, {"data": "test"})
        assert result == {"result": "test result"}


@pytest.mark.asyncio
async def test_script_execution(mock_transport):
    client = MCPClient()
    config = PythonScriptConfig(
        name="Test Script",
        type=MCPType.PYTHON_SCRIPT,
        input_variables=["input"],
        script_path="test.py",
        requirements=["requests>=2.31.0"],
        virtual_env=True,
        timeout=300,
        id="script-1"
    )
    async with httpx.AsyncClient(transport=mock_transport) as ac:
        client._async_client = ac
        result = await client.execute_script(config, {"input": "test"})
        assert result == {"result": "test result"}


@pytest.mark.asyncio
async def test_error_handling():
    def handler(request: Request):
        return Response(400, json={"error": "Bad request"})
    transport = MockTransport(handler)
    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
        id="llm-2"
    )
    async with httpx.AsyncClient(transport=transport) as ac:
        client._async_client = ac
        with pytest.raises(MCPValidationError):
            await client.execute_llm_prompt(config, {"text": "prompt"})


@pytest.mark.asyncio
async def test_timeout_handling():
    def handler(request: Request):
        raise httpx.TimeoutException("Timeout!")
    transport = MockTransport(handler)
    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
        id="llm-3"
    )
    async with httpx.AsyncClient(transport=transport) as ac:
        client._async_client = ac
        with pytest.raises(httpx.TimeoutException):
            await client.execute_llm_prompt(config, {"text": "prompt"})


@pytest.mark.asyncio
async def test_connection_error_handling():
    def handler(request: Request):
        raise httpx.ConnectError("Connection error!")
    transport = MockTransport(handler)
    client = MCPClient()
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Test {text}",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000,
        id="llm-4"
    )
    async with httpx.AsyncClient(transport=transport) as ac:
        client._async_client = ac
        with pytest.raises(httpx.ConnectError):
            await client.execute_llm_prompt(config, {"text": "prompt"})
