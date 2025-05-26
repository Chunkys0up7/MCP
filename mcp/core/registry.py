import uuid
from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session

from mcp.db.models import MCP, MCPVersion
from mcp.schemas.mcp import MCPCreate, MCPUpdate

from .ai_assistant import AIAssistantMCP
# Imports needed from mcp.core for MCP instantiation
from .base import BaseMCPServer
from .jupyter_notebook import JupyterNotebookMCP
from .llm_prompt import LLMPromptMCP
from .python_script import PythonScriptMCP
from .types import MCPType  # Union of all config types
from .types import (AIAssistantConfig, JupyterNotebookConfig, LLMPromptConfig,
                    PythonScriptConfig)

# MCP server registry and persistence
# STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / ".mcp_data" # Adjusted path relative to this file
# STORAGE_DIR.mkdir(exist_ok=True)
# MCP_STORAGE_FILE = STORAGE_DIR / "mcp_storage.json"

# def save_mcp_servers(servers: Dict[str, Dict[str, Any]]): # Removed function
# ... (content of function removed)

# Initialize the global registry
mcp_server_registry: Dict[str, Dict[str, Any]] = {}  # Initialize as empty dict for now
# print(f"MCP Server Registry initialized with {len(mcp_server_registry)} servers from {MCP_STORAGE_FILE}") # Removed print
print(
    "MCP Server Registry initialized as empty. DB loading pending."
)  # Placeholder print

# Initialize embedding model (ensure this model is downloaded/available)
# Using a smaller, efficient model for local dev. Consider larger models for production.
try:
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
except Exception as e:
    print(
        f"Error loading SentenceTransformer model: {e}. Semantic search features might not work."
    )
    embedding_model = None


def load_mcp_definition_from_db(db: Session, mcp_id_str: str) -> Optional[MCP]:
    """Loads a single MCP definition from the database by its ID."""
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        # Invalid UUID format
        return None
    return db.query(MCP).filter(MCP.id == mcp_uuid).first()


def load_all_mcp_definitions_from_db(db: Session) -> List[MCP]:
    """Loads all MCP definitions from the database."""
    return db.query(MCP).all()


def _generate_mcp_embedding(
    mcp_data: MCPCreate | MCPUpdate | MCP, existing_mcp: Optional[MCP] = None
):
    if not embedding_model:
        return None

    text_parts = []
    # For MCPCreate or MCPUpdate, mcp_data has the fields directly
    if isinstance(mcp_data, (MCPCreate, MCPUpdate)):
        text_parts.append(mcp_data.name or "")  # MCPUpdate name can be None
        if mcp_data.description:
            text_parts.append(mcp_data.description)
        if mcp_data.tags:
            text_parts.extend(mcp_data.tags)
    elif isinstance(mcp_data, MCP):
        # For an existing MCP model instance
        text_parts.append(mcp_data.name or "")
        if mcp_data.description:
            text_parts.append(mcp_data.description)
        if mcp_data.tags:
            text_parts.extend(
                mcp_data.tags
            )  # Assuming tags are already a list of strings

    # If it's an update and some fields are not provided, use existing MCP's values if available
    if isinstance(mcp_data, MCPUpdate) and existing_mcp:
        if mcp_data.name is None and existing_mcp.name:
            # If name was in text_parts due to mcp_data.name being None initially then being set to empty string,
            # ensure we don't double add. A bit complex, simpler to reconstruct text_parts for update.
            current_name = existing_mcp.name
        else:
            current_name = mcp_data.name or (existing_mcp.name if existing_mcp else "")

        current_description = (
            mcp_data.description
            if mcp_data.description is not None
            else (existing_mcp.description if existing_mcp else None)
        )
        current_tags = (
            mcp_data.tags
            if mcp_data.tags is not None
            else (existing_mcp.tags if existing_mcp else [])
        )

        text_parts = [current_name or ""]
        if current_description:
            text_parts.append(current_description)
        if current_tags:
            text_parts.extend(current_tags)

    if not any(text_parts):
        return None

    full_text = " ".join(filter(None, text_parts))
    if not full_text.strip():
        return None

    embedding = embedding_model.encode(full_text)
    return embedding.tolist()  # pgvector expects a list or numpy array


def save_mcp_definition_to_db(db: Session, mcp_data: MCPCreate) -> MCP:
    """Saves a new MCP definition and its initial version to the database.
    Performs type-specific validation on the initial_config.
    """

    # Type-specific config validation
    mcp_type_enum = mcp_data.type
    if mcp_type_enum not in _MCP_TYPE_TO_CLASS_AND_CONFIG:
        raise ValueError(f"Unknown MCPType: {mcp_type_enum}. Cannot validate config.")

    _, config_class = _MCP_TYPE_TO_CLASS_AND_CONFIG[mcp_type_enum]

    try:
        # Validate and parse the initial_config using the specific MCP's config model
        # Pydantic will raise ValidationError if initial_config doesn't match config_class
        validated_initial_config = config_class(**mcp_data.initial_config)
    except Exception as e:  # Catch Pydantic ValidationError or other issues
        # Consider more specific exception handling for ValidationError if needed
        raise ValueError(f"Invalid initial_config for MCP type {mcp_type_enum}: {e}")

    db_mcp = MCP(
        name=mcp_data.name,
        type=mcp_data.type.value,  # Use enum value
        description=mcp_data.description,
        tags=mcp_data.tags,
        # Embedding will be set below
    )

    # Generate and set embedding
    embedding = _generate_mcp_embedding(mcp_data)
    if embedding:
        db_mcp.embedding = embedding

    # The MCP ID is generated upon instantiation if default=uuid.uuid4 is set in model

    db_initial_version = MCPVersion(
        mcp=db_mcp,  # Associate with the MCP object
        version_str=mcp_data.initial_version_str,
        description=mcp_data.initial_version_description,
        config_snapshot=validated_initial_config.model_dump(),  # Store the validated and structured config
    )

    # Add MCP first, so it gets an ID if not already set by default factory (though it should)
    db.add(db_mcp)
    # Then add version. Cascading might handle this, but explicit add is fine.
    db.add(db_initial_version)

    try:
        db.commit()
        db.refresh(db_mcp)
        # db.refresh(db_initial_version) # Optional: refresh if you need its generated fields immediately
    except Exception as e:  # Catch potential DB errors
        db.rollback()
        # Consider logging the error e
        # Consider raising a custom exception or re-raising
        raise e  # Re-raise for now, API layer can handle it
    return db_mcp


def update_mcp_definition_in_db(
    db: Session, mcp_id_str: str, mcp_data: MCPUpdate
) -> Optional[MCP]:
    """Updates an existing MCP definition in the database."""
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        return None

    db_mcp = db.query(MCP).filter(MCP.id == mcp_uuid).first()
    if not db_mcp:
        return None

    update_data = mcp_data.model_dump(exclude_unset=True)
    needs_embedding_update = False
    for key, value in update_data.items():
        if key in ["name", "description", "tags"] and getattr(db_mcp, key) != value:
            needs_embedding_update = True
        setattr(db_mcp, key, value)

    if needs_embedding_update:
        # Pass the db_mcp instance itself which now has updated fields (prior to commit)
        # Or pass mcp_data with existing_mcp=db_mcp to _generate_mcp_embedding
        embedding = _generate_mcp_embedding(
            mcp_data, existing_mcp=db_mcp
        )  # Pass mcp_data and original db_mcp
        if embedding:
            db_mcp.embedding = embedding

    try:
        db.commit()
        db.refresh(db_mcp)
    except Exception as e:
        db.rollback()
        raise e
    return db_mcp


def delete_mcp_definition_from_db(db: Session, mcp_id_str: str) -> bool:
    """Deletes an MCP definition from the database.
    Note: MCPVersions associated with this MCP will also be deleted due to cascade settings.
    """
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        return False  # Invalid ID format

    db_mcp = db.query(MCP).filter(MCP.id == mcp_uuid).first()
    if not db_mcp:
        return False  # MCP not found

    try:
        db.delete(db_mcp)
        db.commit()
    except Exception as e:
        db.rollback()
        # Log error e
        raise e  # Or return False, depending on desired error handling
    return True


# Helper to map MCPType enum to MCP Server class and its config type
_MCP_TYPE_TO_CLASS_AND_CONFIG = {
    MCPType.LLM_PROMPT: (LLMPromptMCP, LLMPromptConfig),
    MCPType.JUPYTER_NOTEBOOK: (JupyterNotebookMCP, JupyterNotebookConfig),
    MCPType.PYTHON_SCRIPT: (PythonScriptMCP, PythonScriptConfig),
    MCPType.AI_ASSISTANT: (AIAssistantMCP, AIAssistantConfig),
}


def get_mcp_instance_from_db(
    db: Session, mcp_id_str: str, mcp_version_str: Optional[str] = None
) -> Optional[BaseMCPServer]:
    """
    Fetches an MCP definition and its specific version (or latest if version_str is None)
    from the database and returns an instantiated MCP server.

    Args:
        db: The SQLAlchemy session.
        mcp_id_str: The string UUID of the MCP definition.
        mcp_version_str: The optional version string (e.g., "1.0.0", "latest").
                         If None or "latest", the most recent version is fetched.

    Returns:
        An instantiated BaseMCPServer subclass, or None if not found or on error.
    """
    try:
        mcp_uuid = uuid.UUID(mcp_id_str)
    except ValueError:
        # Log error: Invalid mcp_id_str format
        return None

    # Fetch the MCP definition to get its type
    mcp_definition = db.query(MCP).filter(MCP.id == mcp_uuid).first()
    if not mcp_definition:
        # Log error: MCP definition not found
        return None

    # Determine which version to fetch
    query = db.query(MCPVersion).filter(MCPVersion.mcp_id == mcp_uuid)
    if mcp_version_str and mcp_version_str.lower() != "latest":
        query = query.filter(MCPVersion.version_str == mcp_version_str)
    else:
        # Order by created_at or a semantic version sort key if available
        # For simplicity, assuming version_str can be lexicographically sorted for "latest",
        # or a dedicated "is_latest" flag or a proper version sorting mechanism exists.
        # If version_str is like "1.0.0", "1.1.0", direct string sort might not be ideal.
        # Using a 'created_at' timestamp for ordering versions is safer for "latest".
        # Assuming MCPVersion has a 'created_at' field (it should for good version tracking)
        # If MCPVersion has 'created_at' field uncomment below:
        # query = query.order_by(MCPVersion.created_at.desc())
        # For now, if no explicit version, and no created_at, we might get an arbitrary one or error.
        # Let's assume for now we need a specific version or a clear latest marker in a real scenario.
        # If we need to strictly get the latest version, we'd need to enhance this query.
        # For this example, if no version_str, it tries to get any version.
        # A robust solution would order by a version sequence or timestamp.
        # Let's assume for now, if mcp_version_str is None, we attempt to get the one with the highest ID or a specific 'latest' tag.
        # This part needs to be robust based on how versions are managed (e.g., semantic versioning, 'latest' tag, creation timestamp).
        # For now, we will fetch the first one if no version is specified, or the one matching the version string.
        # A better way for "latest" would be to sort by a version index or creation date.
        query = query.order_by(
            MCPVersion.id.desc()
        )  # Placeholder for a proper "latest" logic

    mcp_version = query.first()

    if not mcp_version:
        # Log error: MCP version not found
        return None

    config_snapshot = mcp_version.config_snapshot
    mcp_type_str = mcp_definition.type  # This is stored as string from enum value

    try:
        mcp_type_enum = MCPType(
            mcp_type_str
        )  # Convert string back to MCPType enum member
    except ValueError:
        # Log error: Invalid MCP type string in DB
        return None

    if mcp_type_enum not in _MCP_TYPE_TO_CLASS_AND_CONFIG:
        # Log error: Unknown MCP type or not registered
        return None

    mcp_class, config_class = _MCP_TYPE_TO_CLASS_AND_CONFIG[mcp_type_enum]

    try:
        # Validate and parse the config_snapshot using the specific MCP's config model
        # Pydantic will raise ValidationError if config_snapshot doesn't match config_class
        # For example, if config_snapshot is a dict, Pydantic will try to create config_class(**config_snapshot)
        if isinstance(config_snapshot, dict):
            parsed_config = config_class(
                **config_snapshot
            )  # This is the Pydantic model for the config
        elif isinstance(
            config_snapshot, config_class
        ):  # If already a Pydantic model (less likely from DB raw)
            parsed_config = config_snapshot
        else:
            # Log error: config_snapshot is not a dict or the expected Pydantic model type
            return None

        # Instantiate the MCP server with the parsed and validated configuration
        mcp_instance = mcp_class(config=parsed_config)
        # Note: The MCP class's __init__ should expect a single 'config' argument
        # which is an instance of its specific config model (e.g., LLMPromptConfig).
        # If the MCP class expects individual config values in its __init__,
        # then this instantiation needs to change: mcp_class(**parsed_config.model_dump())

        # It's also good practice for BaseMCPServer (or individual MCPs) to store their definition ID and version ID
        # mcp_instance.mcp_definition_id = mcp_definition.id
        # mcp_instance.mcp_version_id = mcp_version.id

        return mcp_instance
    except Exception:
        # Log error during config parsing or MCP instantiation (e.g., Pydantic ValidationError)
        # print(f"Error instantiating MCP {mcp_id_str} version {mcp_version_str}: {e}")
        return None


def search_mcp_definitions_by_text(
    db: Session, query_text: str, limit: int = 10
) -> List[MCP]:
    """Searches for MCP definitions using semantic similarity of the query_text to MCP embeddings."""
    if not embedding_model:
        # Log or raise error: embedding model not available
        return []
    if not query_text or not query_text.strip():
        return []

    query_embedding = embedding_model.encode(query_text)

    # Assuming MCP model has an 'embedding' field of type Vector
    # and pgvector extension is enabled with appropriate distance function.
    # Using cosine distance: 0 is most similar, 1 is least similar.
    # For other distances like L2, smaller is better.
    # results = db.query(MCP).order_by(MCP.embedding.l2_distance(query_embedding)).limit(limit).all()
    results = (
        db.query(MCP)
        .order_by(MCP.embedding.cosine_distance(query_embedding))
        .limit(limit)
        .all()
    )
    return results
