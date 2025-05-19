import pytest
from mcp.core.types import (
    MCPType,
    BaseMCPConfig,
    LLMPromptConfig,
    JupyterNotebookConfig,
    PythonScriptConfig
)

def test_mcp_type_enum():
    """Test MCPType enum values."""
    assert MCPType.LLM_PROMPT.value == "llm_prompt"
    assert MCPType.JUPYTER_NOTEBOOK.value == "jupyter_notebook"
    assert MCPType.PYTHON_SCRIPT.value == "python_script"
    assert MCPType.AI_ASSISTANT.value == "ai_assistant"

def test_base_mcp_config():
    """Test BaseMCPConfig creation and validation."""
    config = BaseMCPConfig(
        name="Test Base",
        type=MCPType.LLM_PROMPT,
        input_variables=["var1", "var2"]
    )
    assert config.type == MCPType.LLM_PROMPT
    assert config.input_variables == ["var1", "var2"]

def test_llm_prompt_config():
    """Test LLMPromptConfig creation and validation."""
    config = LLMPromptConfig(
        name="Test LLM",
        type=MCPType.LLM_PROMPT,
        input_variables=["text"],
        template="Analyze: {text}",
        system_prompt="You are a helpful assistant",
        model_name="claude-3-sonnet-20240229",
        temperature=0.7,
        max_tokens=1000
    )
    assert config.type == MCPType.LLM_PROMPT
    assert config.template == "Analyze: {text}"
    assert config.system_prompt == "You are a helpful assistant"
    assert config.model_name == "claude-3-sonnet-20240229"
    assert config.temperature == 0.7
    assert config.max_tokens == 1000

def test_jupyter_notebook_config():
    """Test JupyterNotebookConfig creation and validation."""
    config = JupyterNotebookConfig(
        name="Test Notebook",
        type=MCPType.JUPYTER_NOTEBOOK,
        input_variables=["data"],
        notebook_path="test.ipynb",
        execute_all=True,
        timeout=600
    )
    assert config.type == MCPType.JUPYTER_NOTEBOOK
    assert config.notebook_path == "test.ipynb"
    assert config.execute_all is True
    assert config.cells_to_execute is None
    assert config.timeout == 600

def test_python_script_config():
    """Test PythonScriptConfig creation and validation."""
    config = PythonScriptConfig(
        name="Test Script",
        type=MCPType.PYTHON_SCRIPT,
        input_variables=["input"],
        script_path="test.py",
        requirements=["requests>=2.31.0"],
        virtual_env=True,
        timeout=300
    )
    assert config.type == MCPType.PYTHON_SCRIPT
    assert config.script_path == "test.py"
    assert config.requirements == ["requests>=2.31.0"]
    assert config.virtual_env is True
    assert config.timeout == 300

def test_config_validation():
    """Test configuration validation."""
    # Test invalid temperature
    with pytest.raises(ValueError):
        LLMPromptConfig(
            name="Invalid Temp",
            type=MCPType.LLM_PROMPT,
            input_variables=["text"],
            template="Test",
            model_name="claude-3-sonnet-20240229",
            temperature=1.5,  # Invalid temperature
            max_tokens=1000
        )

    # Test invalid timeout
    with pytest.raises(ValueError):
        JupyterNotebookConfig(
            name="Invalid Timeout",
            type=MCPType.JUPYTER_NOTEBOOK,
            input_variables=["data"],
            notebook_path="test.ipynb",
            execute_all=True,
            timeout=-1  # Invalid timeout
        )

    # Test missing required field
    with pytest.raises(ValueError):
        PythonScriptConfig(
            name="Missing Requirements",
            type=MCPType.PYTHON_SCRIPT,
            input_variables=["input"],
            script_path="test.py",
            # Missing requirements
            virtual_env=True,
            timeout=300
        ) 