import pytest
from mcp.db.operations import DatabaseOperations

def test_postgres_crud(db_session):
    """Test PostgreSQL CRUD operations."""
    ops = DatabaseOperations(db_session)
    # Create a test configuration
    test_config = {
        "type": "prompt",
        "template": "Test template",
        "model": "test-model"
    }
    config = ops.create_configuration(
        name="Test Config",
        type="prompt",
        config=test_config
    )
    assert config.id is not None
    # Retrieve the configuration
    retrieved = ops.get_configuration(config.id)
    assert retrieved is not None
    assert retrieved.name == "Test Config"
    assert retrieved.config["template"] == "Test template"
    # Clean up
    assert ops.delete_configuration(config.id) 