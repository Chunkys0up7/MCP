import uuid
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from mcp.core import registry as mcp_registry_service
from mcp.core.types import MCPType
from mcp.db.models import EMBEDDING_DIM
from mcp.db.models import MCP as MCPModel
from mcp.db.models import MCPVersion as MCPVersionModel
from mcp.schemas.mcp import MCPCreate as MCPCreateSchema
from mcp.schemas.mcp import MCPUpdate as MCPUpdateSchema

# Fixture for a mock DB session (if not using the actual test_db_session from conftest for some tests)
# For most registry tests, interacting with the actual in-memory DB is preferable.


@pytest.fixture
def basic_mcp_create_payload() -> MCPCreateSchema:
    return MCPCreateSchema(
        name="Test Registry MCP",
        type=MCPType.PYTHON_SCRIPT,
        description="A test MCP for registry functions.",
        tags=["registry", "python"],
        initial_version_str="1.0.0",
        initial_version_description="Initial version for registry test",
        initial_config={"script_content": "print('Hello from registry test')"},
    )


# === Tests for save_mcp_definition_to_db ===
def test_save_mcp_definition_to_db_success(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    created_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=basic_mcp_create_payload
    )

    assert created_mcp is not None
    assert created_mcp.name == basic_mcp_create_payload.name
    assert created_mcp.type == basic_mcp_create_payload.type.value
    assert created_mcp.description == basic_mcp_create_payload.description
    assert created_mcp.tags == basic_mcp_create_payload.tags
    assert created_mcp.embedding is not None
    assert len(created_mcp.embedding) == EMBEDDING_DIM

    assert len(created_mcp.versions) == 1
    version = created_mcp.versions[0]
    assert version.version_str == basic_mcp_create_payload.initial_version_str
    assert (
        version.config_snapshot["script_content"]
        == basic_mcp_create_payload.initial_config["script_content"]
    )

    # Verify it's actually in the DB
    retrieved_mcp = (
        test_db_session.query(MCPModel).filter(MCPModel.id == created_mcp.id).first()
    )
    assert retrieved_mcp is not None
    assert retrieved_mcp.name == basic_mcp_create_payload.name


def test_save_mcp_definition_to_db_invalid_config(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    invalid_config_payload = basic_mcp_create_payload.model_copy()
    invalid_config_payload.initial_config = {
        "wrong_key": "for_python_script"
    }  # Invalid for PythonScriptConfig

    with pytest.raises(
        ValueError, match="Invalid initial_config for MCP type python_script"
    ):
        mcp_registry_service.save_mcp_definition_to_db(
            db=test_db_session, mcp_data=invalid_config_payload
        )


@patch(
    "mcp.core.registry.embedding_model", None
)  # Simulate embedding model not loading
def test_save_mcp_definition_to_db_no_embedding_model(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    created_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=basic_mcp_create_payload
    )
    assert created_mcp.embedding is None


# === Tests for load_mcp_definition_from_db ===
def test_load_mcp_definition_from_db_found(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    created_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=basic_mcp_create_payload
    )

    loaded_mcp = mcp_registry_service.load_mcp_definition_from_db(
        db=test_db_session, mcp_id_str=str(created_mcp.id)
    )
    assert loaded_mcp is not None
    assert loaded_mcp.id == created_mcp.id
    assert loaded_mcp.name == created_mcp.name


def test_load_mcp_definition_from_db_not_found(test_db_session: Session):
    non_existent_id = str(uuid.uuid4())
    loaded_mcp = mcp_registry_service.load_mcp_definition_from_db(
        db=test_db_session, mcp_id_str=non_existent_id
    )
    assert loaded_mcp is None


def test_load_mcp_definition_from_db_invalid_uuid(test_db_session: Session):
    loaded_mcp = mcp_registry_service.load_mcp_definition_from_db(
        db=test_db_session, mcp_id_str="not-a-uuid"
    )
    assert loaded_mcp is None


# === Tests for load_all_mcp_definitions_from_db ===
def test_load_all_mcp_definitions_from_db_empty(test_db_session: Session):
    mcps = mcp_registry_service.load_all_mcp_definitions_from_db(db=test_db_session)
    assert mcps == []


def test_load_all_mcp_definitions_from_db_with_data(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    mcp1_payload = basic_mcp_create_payload.model_copy()
    mcp1_payload.name = "MCP One"
    mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=mcp1_payload
    )

    mcp2_payload = basic_mcp_create_payload.model_copy()
    mcp2_payload.name = "MCP Two"
    mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=mcp2_payload
    )

    mcps = mcp_registry_service.load_all_mcp_definitions_from_db(db=test_db_session)
    assert len(mcps) == 2
    assert {m.name for m in mcps} == {"MCP One", "MCP Two"}


# === Tests for update_mcp_definition_in_db ===
def test_update_mcp_definition_in_db_success(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    created_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=basic_mcp_create_payload
    )
    original_embedding = created_mcp.embedding

    update_payload = MCPUpdateSchema(
        name="Updated Registry MCP Name",
        description="Updated description.",
        tags=["updated_tag"],
    )
    updated_mcp = mcp_registry_service.update_mcp_definition_in_db(
        db=test_db_session, mcp_id_str=str(created_mcp.id), mcp_data=update_payload
    )

    assert updated_mcp is not None
    assert updated_mcp.id == created_mcp.id
    assert updated_mcp.name == update_payload.name
    assert updated_mcp.description == update_payload.description
    assert updated_mcp.tags == update_payload.tags
    assert (
        updated_mcp.type == basic_mcp_create_payload.type.value
    )  # Type should not change

    # Check if embedding was updated
    assert updated_mcp.embedding is not None
    assert (
        updated_mcp.embedding != original_embedding
    )  # Assuming name/desc/tags change leads to new embedding
    assert len(updated_mcp.embedding) == EMBEDDING_DIM


def test_update_mcp_definition_in_db_no_change_no_embedding_update(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    created_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=basic_mcp_create_payload
    )
    test_db_session.commit()  # Ensure embedding is persisted
    test_db_session.refresh(created_mcp)
    original_embedding = created_mcp.embedding
    assert original_embedding is not None

    update_payload = MCPUpdateSchema(
        name=created_mcp.name
    )  # No actual change to name, desc, or tags

    updated_mcp = mcp_registry_service.update_mcp_definition_in_db(
        db=test_db_session, mcp_id_str=str(created_mcp.id), mcp_data=update_payload
    )
    assert updated_mcp is not None
    # Depending on implementation, if only non-text fields are "updated" to same values,
    # embedding might not be re-calculated. The current logic in update_mcp_definition_in_db
    # checks if getattr(db_mcp, key) != value. If they are same, needs_embedding_update remains false.
    assert updated_mcp.embedding == original_embedding


def test_update_mcp_definition_in_db_not_found(test_db_session: Session):
    non_existent_id = str(uuid.uuid4())
    update_payload = MCPUpdateSchema(name="Doesn't matter")
    updated_mcp = mcp_registry_service.update_mcp_definition_in_db(
        db=test_db_session, mcp_id_str=non_existent_id, mcp_data=update_payload
    )
    assert updated_mcp is None


# === Tests for delete_mcp_definition_from_db ===
def test_delete_mcp_definition_from_db_success(
    test_db_session: Session, basic_mcp_create_payload: MCPCreateSchema
):
    created_mcp = mcp_registry_service.save_mcp_definition_to_db(
        db=test_db_session, mcp_data=basic_mcp_create_payload
    )
    mcp_id = created_mcp.id
    assert (
        test_db_session.query(MCPModel).filter(MCPModel.id == mcp_id).first()
        is not None
    )

    deleted = mcp_registry_service.delete_mcp_definition_from_db(
        db=test_db_session, mcp_id_str=str(mcp_id)
    )
    assert deleted is True
    assert test_db_session.query(MCPModel).filter(MCPModel.id == mcp_id).first() is None
    # Check if versions are also deleted (cascade)
    assert (
        test_db_session.query(MCPVersionModel)
        .filter(MCPVersionModel.mcp_id == mcp_id)
        .count()
        == 0
    )


def test_delete_mcp_definition_from_db_not_found(test_db_session: Session):
    non_existent_id = str(uuid.uuid4())
    deleted = mcp_registry_service.delete_mcp_definition_from_db(
        db=test_db_session, mcp_id_str=non_existent_id
    )
    assert deleted is False


# === Tests for _generate_mcp_embedding ===
# Patch the global embedding_model in the registry module for these tests
@patch("mcp.core.registry.embedding_model")
def test_generate_mcp_embedding_with_mcp_create(
    mock_embedding_model_global, basic_mcp_create_payload: MCPCreateSchema
):
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = [0.1] * EMBEDDING_DIM  # Mock embedding output
    mock_embedding_model_global.encode = mock_encoder  # Attach to the .encode attribute

    embedding = mcp_registry_service._generate_mcp_embedding(basic_mcp_create_payload)
    assert embedding is not None
    assert len(embedding) == EMBEDDING_DIM
    expected_text = (
        "Test Registry MCP A test MCP for registry functions. registry python"
    )
    mock_embedding_model_global.encode.assert_called_once_with(expected_text)


@patch("mcp.core.registry.embedding_model")
def test_generate_mcp_embedding_with_mcp_update(mock_embedding_model_global):
    mock_encoder = MagicMock()
    mock_encoder.encode.return_value = [0.2] * EMBEDDING_DIM
    mock_embedding_model_global.encode = mock_encoder

    update_payload = MCPUpdateSchema(name="Updated Name", description="New desc")
    # Simulate existing MCP for context
    existing_mcp_mock = MCPModel(
        id=uuid.uuid4(),
        name="Original Name",
        description="Original Desc",
        tags=["orig_tag"],
    )

    embedding = mcp_registry_service._generate_mcp_embedding(
        update_payload, existing_mcp=existing_mcp_mock
    )
    assert embedding is not None
    expected_text = "Updated Name New desc orig_tag"
    mock_embedding_model_global.encode.assert_called_once_with(expected_text)


@patch("mcp.core.registry.embedding_model", None)  # Test when model fails to load
def test_generate_mcp_embedding_no_model(basic_mcp_create_payload: MCPCreateSchema):
    embedding = mcp_registry_service._generate_mcp_embedding(basic_mcp_create_payload)
    assert embedding is None


def test_generate_mcp_embedding_empty_input():
    empty_payload = MCPCreateSchema(
        name="",
        type=MCPType.PYTHON_SCRIPT,
        initial_version_str="1",
        initial_config={"script_content": ""},
        description="",
        tags=[],
    )
    embedding = mcp_registry_service._generate_mcp_embedding(empty_payload)
    assert embedding is None  # Should return None if all text parts are empty


# === Tests for search_mcp_definitions_by_text ===
@patch("mcp.core.registry.embedding_model")
def test_search_mcp_definitions_by_text_success(
    mock_embedding_model_global, test_db_session: Session
):
    mock_encoder = MagicMock()
    mock_query_embedding = [0.3] * EMBEDDING_DIM
    mock_encoder.encode.return_value = mock_query_embedding
    mock_embedding_model_global.encode = mock_encoder

    # Mock the database query result
    # We can't easily test the .cosine_distance part with SQLite, so we mock the final DB call result
    mock_db_mcps = [
        MCPModel(
            id=uuid.uuid4(), name="Search Result 1", embedding=[0.31] * EMBEDDING_DIM
        ),
        MCPModel(
            id=uuid.uuid4(), name="Search Result 2", embedding=[0.32] * EMBEDDING_DIM
        ),
    ]

    with patch.object(test_db_session, "query") as mock_db_query:
        mock_query_chain = MagicMock()
        mock_db_query.return_value = mock_query_chain  # query(MCP)
        mock_query_chain.order_by.return_value = mock_query_chain  # .order_by(...)
        mock_query_chain.limit.return_value = mock_query_chain  # .limit(...)
        mock_query_chain.all.return_value = mock_db_mcps  # .all()

        results = mcp_registry_service.search_mcp_definitions_by_text(
            test_db_session, "test query", limit=5
        )

        assert len(results) == 2
        assert results[0].name == "Search Result 1"
        mock_embedding_model_global.encode.assert_called_once_with("test query")
        mock_db_query.assert_called_once_with(MCPModel)
        # We can't easily assert the content of order_by due to complex object,
        # but we check it was called, and limit and all were called.
        mock_query_chain.order_by.assert_called_once()
        mock_query_chain.limit.assert_called_once_with(5)
        mock_query_chain.all.assert_called_once()


@patch("mcp.core.registry.embedding_model", None)
def test_search_mcp_definitions_by_text_no_model(test_db_session: Session):
    results = mcp_registry_service.search_mcp_definitions_by_text(
        test_db_session, "test query"
    )
    assert results == []


def test_search_mcp_definitions_by_text_empty_query(test_db_session: Session):
    results = mcp_registry_service.search_mcp_definitions_by_text(
        test_db_session, "   "
    )
    assert results == []


# Final placeholder for get_mcp_instance_from_db if direct unit tests are still desired.
# As noted, it's fairly well covered by engine and API integration tests.

# More tests to be added for get_mcp_instance_from_db
