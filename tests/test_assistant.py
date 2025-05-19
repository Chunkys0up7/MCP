import pytest
from unittest.mock import patch, MagicMock
from mcp.core.types import AIAssistantConfig, MCPType
from mcp.api.assistant import AIAssistant

@pytest.fixture
def assistant_config():
    """Create test assistant configuration."""
    return AIAssistantConfig(
        name="Test Assistant",
        type=MCPType.AI_ASSISTANT,
        input_variables=[],
        model_name="claude-3-sonnet-20240229",
        system_prompt="You are a helpful assistant.",
        temperature=0.7,
        max_tokens=1000,
        memory_size=5,
        tools=[
            {
                'name': 'test_tool',
                'description': 'Test tool',
                'parameters': {
                    'param1': {'type': 'str', 'required': True},
                    'param2': {'type': 'int', 'required': False}
                }
            }
        ],
        tool_choice="auto"
    )

@pytest.fixture
def assistant(assistant_config):
    """Create test assistant instance."""
    return AIAssistant(assistant_config)

def test_assistant_initialization(assistant_config):
    """Test assistant initialization."""
    assistant = AIAssistant(assistant_config)
    assert assistant.config == assistant_config
    assert len(assistant.memory) == 0
    assert len(assistant.tools) == 1
    assert assistant.tools[0]['name'] == 'test_tool'

def test_add_to_memory(assistant):
    """Test adding message to memory."""
    message = {'role': 'user', 'content': 'test message'}
    assistant.add_to_memory(message)
    assert len(assistant.memory) == 1
    assert assistant.memory[0]['message'] == message
    assert 'timestamp' in assistant.memory[0]

def test_memory_size_limit(assistant):
    """Test memory size limit."""
    # Add more messages than memory size
    for i in range(10):
        assistant.add_to_memory({'role': 'user', 'content': f'message {i}'})
    
    # Verify memory is trimmed
    assert len(assistant.memory) == assistant.config.memory_size
    assert assistant.memory[0]['message']['content'] == 'message 5'

def test_clear_memory(assistant):
    """Test clearing memory."""
    assistant.add_to_memory({'role': 'user', 'content': 'test message'})
    assistant.clear_memory()
    assert len(assistant.memory) == 0

@pytest.mark.asyncio
async def test_execute_tool(assistant):
    """Test tool execution."""
    result = await assistant.execute_tool('test_tool', {'param1': 'test'})
    assert result['status'] == 'success'
    assert 'result' in result

@pytest.mark.asyncio
async def test_execute_tool_validation(assistant):
    """Test tool execution parameter validation."""
    # Missing required parameter
    with pytest.raises(ValueError) as exc_info:
        await assistant.execute_tool('test_tool', {})
    assert "Required parameter" in str(exc_info.value)
    
    # Invalid parameter type
    with pytest.raises(ValueError) as exc_info:
        await assistant.execute_tool('test_tool', {'param1': 123})
    assert "must be of type" in str(exc_info.value)
    
    # Unknown parameter
    with pytest.raises(ValueError) as exc_info:
        await assistant.execute_tool('test_tool', {'param1': 'test', 'unknown': 'value'})
    assert "Unknown parameter" in str(exc_info.value)

@pytest.mark.asyncio
async def test_process_message(assistant):
    """Test message processing."""
    response = await assistant.process_message("test message")
    assert response['role'] == 'assistant'
    assert 'content' in response
    assert len(assistant.memory) == 2  # User message and assistant response

def test_get_tools(assistant):
    """Test getting tools."""
    tools = assistant.get_tools()
    assert len(tools) == 1
    assert tools[0]['name'] == 'test_tool'

def test_add_tool(assistant):
    """Test adding tool."""
    new_tool = {
        'name': 'new_tool',
        'description': 'New tool',
        'parameters': {
            'param': {'type': 'str', 'required': True}
        }
    }
    assistant.add_tool(new_tool)
    assert len(assistant.tools) == 2
    assert assistant.tools[1]['name'] == 'new_tool'

def test_remove_tool(assistant):
    """Test removing tool."""
    assistant.remove_tool('test_tool')
    assert len(assistant.tools) == 0

def test_validate_tools():
    """Test tool validation."""
    import pydantic
    config = None
    with pytest.raises((ValueError, pydantic.ValidationError)) as exc_info:
        config = AIAssistantConfig(
            name="Invalid Assistant",
            type=MCPType.AI_ASSISTANT,
            input_variables=[],
            model_name="claude-3-sonnet-20240229",
            system_prompt="Test",
            tools=[
                {
                    'name': 'valid_tool',
                    'description': 'Valid tool',
                    'parameters': {'param': {'type': 'str', 'required': True}}
                },
                {
                    'name': 'invalid_tool',
                    'description': 'Invalid tool'
                    # Missing parameters
                }
            ]
        )
    assert "Tool must have parameters" in str(exc_info.value)

def test_tool_choice_validation():
    """Test tool choice validation."""
    with pytest.raises(ValueError) as exc_info:
        AIAssistantConfig(
            name="Invalid Tool Choice",
            type=MCPType.AI_ASSISTANT,
            input_variables=[],
            model_name="claude-3-sonnet-20240229",
            system_prompt="Test",
            tool_choice="invalid"  # Invalid tool choice
        )
    assert "Tool choice must be one of" in str(exc_info.value) 