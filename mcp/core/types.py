from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

class MCPType(str, Enum):
    """Types of MCP servers."""
    LLM_PROMPT = "llm_prompt"
    JUPYTER_NOTEBOOK = "jupyter_notebook"
    PYTHON_SCRIPT = "python_script"
    AI_ASSISTANT = "ai_assistant"

class BaseMCPConfig(BaseModel):
    """Base configuration for all MCP types."""
    name: str
    type: MCPType
    description: Optional[str] = None
    input_variables: List[str] = Field(default_factory=list)

class LLMPromptConfig(BaseMCPConfig):
    """Configuration for LLM Prompt MCP."""
    type: MCPType = MCPType.LLM_PROMPT
    template: str
    model_name: str = "claude-3-sonnet-20240229"
    temperature: float = Field(ge=0.0, le=1.0, default=0.7)
    max_tokens: int = Field(ge=1, default=1000)
    system_prompt: Optional[str] = None

class JupyterNotebookConfig(BaseMCPConfig):
    """Configuration for Jupyter Notebook MCP."""
    type: MCPType = MCPType.JUPYTER_NOTEBOOK
    notebook_path: str
    execute_all: bool = True
    cells_to_execute: Optional[List[int]] = None
    timeout: int = Field(ge=60, default=600)

class PythonScriptConfig(BaseMCPConfig):
    """Configuration for Python Script MCP."""
    type: MCPType = MCPType.PYTHON_SCRIPT
    script_path: str
    requirements: List[str] = Field(default_factory=list)
    virtual_env: bool = True
    timeout: int = Field(ge=60, default=600)

class AIAssistantConfig(BaseMCPConfig):
    """AI assistant configuration."""
    type: MCPType = MCPType.AI_ASSISTANT
    model_name: str = "claude-3-sonnet-20240229"
    system_prompt: str
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1000, gt=0)
    memory_size: int = Field(default=10, gt=0)
    tools: List[Dict[str, Any]] = Field(default_factory=list)
    tool_choice: str = "auto"
    response_format: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('tools')
    def validate_tools(cls, v):
        """Validate tools configuration."""
        if not v:
            return v
        for tool in v:
            if 'name' not in tool:
                raise ValueError("Tool must have a name")
            if 'description' not in tool:
                raise ValueError("Tool must have a description")
            if 'parameters' not in tool:
                raise ValueError("Tool must have parameters")
        return v

    @validator('tool_choice')
    def validate_tool_choice(cls, v):
        """Validate tool choice."""
        valid_choices = ['auto', 'none']
        if v not in valid_choices:
            raise ValueError(f"Tool choice must be one of {valid_choices}")
        return v

# Union type for all MCP configs
MCPConfig = Union[LLMPromptConfig, JupyterNotebookConfig, PythonScriptConfig, AIAssistantConfig]

class MCPResult(BaseModel):
    """Result from MCP execution."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None 