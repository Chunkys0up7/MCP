# MCP Class Mapping

This document provides a high-level overview of the main classes in the MCP system and their purposes.

## Core Components

### MCP Types and Configuration
- **MCPType**: Defines the different types of components that can be created (like Python scripts, LLM prompts, etc.)
- **BaseMCPConfig**: The basic configuration template that all MCP types must follow
- **LLMPromptConfig**: Configuration for language model prompts, including settings like temperature and model selection
- **PythonScriptConfig**: Configuration for Python scripts, including dependencies and execution settings
- **JupyterNotebookConfig**: Configuration for Jupyter notebooks, including execution settings and cell selection
- **AssistantConfig**: Configuration for AI assistants, including model settings and available tools

### Database Models
- **MCP**: Stores information about MCP components, including their name, type, and description
- **MCPVersion**: Tracks different versions of MCP components and their configurations
- **WorkflowDefinition**: Stores workflow definitions, including steps and their connections
- **WorkflowRun**: Records the execution history of workflows, including results and status
- **ArchitecturalConstraints**: Stores rules and limitations for workflow execution

### API Components
- **MCPClient**: Handles communication with the MCP server, making it easy to create and manage components
- **WorkflowEngine**: Manages the execution of workflows, handling step-by-step processing and error handling
- **MCPRegistry**: Manages the collection of available MCP components and their versions

### Security Components
- **UserRole**: Defines different user roles (like admin, developer, user) and their permissions
- **JWTManager**: Handles the creation and validation of security tokens
- **RBACManager**: Manages role-based access control for different operations

### UI Components
- **PersonalizedFeedScreen**: Shows personalized recommendations and recent activities
- **FacetedSearchScreen**: Provides advanced search capabilities for finding components
- **WorkflowBuilder**: Visual interface for creating and editing workflows
- **ExecutionMonitor**: Shows real-time status of workflow execution

## Utility Components

### Caching
- **RedisCacheManager**: Manages temporary storage of frequently used data
- **CacheConfig**: Configuration settings for the caching system

### Logging and Monitoring
- **Logger**: Handles recording of system events and errors
- **MetricsCollector**: Gathers performance and usage statistics

### Configuration Management
- **Config**: Central configuration manager for the entire system
- **EnvironmentManager**: Handles environment-specific settings

## Integration Components

### External Services
- **LLMService**: Manages communication with language models
- **NotebookExecutor**: Handles execution of Jupyter notebooks
- **ScriptExecutor**: Manages execution of Python scripts

### Data Management
- **EmbeddingGenerator**: Creates searchable representations of components
- **VectorStore**: Stores and manages component embeddings for search

## Helper Classes

### Validation
- **SchemaValidator**: Ensures data follows the correct format
- **InputValidator**: Checks user input for correctness

### Error Handling
- **ErrorHandler**: Manages and formats error messages
- **RetryManager**: Handles automatic retries for failed operations

### Data Processing
- **DataTransformer**: Converts data between different formats
- **ResultFormatter**: Formats execution results for display 