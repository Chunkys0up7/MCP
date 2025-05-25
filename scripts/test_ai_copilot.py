"""
Test script for the AI Co-Pilot functionality.
"""

import sys
import os
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.components.ai_copilot import AICoPilot, SuggestionType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_workflow_analysis():
    """Test workflow analysis functionality."""
    copilot = AICoPilot()
    
    # Test workflow with missing fields
    incomplete_workflow = {
        "name": "test_workflow",
        # Missing version
        "nodes": [
            {
                "id": "node1",
                "type": "task",
                # Missing error handling
            }
        ],
        # Missing edges
    }
    
    suggestions = copilot.analyze_workflow(incomplete_workflow)
    
    # Verify suggestions
    assert any(s.type == SuggestionType.SCHEMA_REPAIR for s in suggestions), "Should detect schema issues"
    assert any(s.type == SuggestionType.BEST_PRACTICE for s in suggestions), "Should detect best practice issues"
    
    logger.info("Workflow analysis test passed")
    return suggestions

def test_error_resolution():
    """Test error resolution suggestion functionality."""
    copilot = AICoPilot()
    
    # Test error data
    error_data = {
        "type": "connection_timeout",
        "message": "Failed to connect to database",
        "node_id": "node1"
    }
    
    suggestions = copilot.suggest_error_resolution(error_data)
    
    # Verify suggestions
    assert all(s.type == SuggestionType.ERROR_RESOLUTION for s in suggestions), "Should provide error resolution suggestions"
    
    logger.info("Error resolution test passed")
    return suggestions

def main():
    """Run all tests."""
    logger.info("Starting AI Co-Pilot tests...")
    
    # Test workflow analysis
    workflow_suggestions = test_workflow_analysis()
    logger.info(f"Workflow suggestions: {len(workflow_suggestions)}")
    for suggestion in workflow_suggestions:
        logger.info(f"- {suggestion.type.value}: {suggestion.description}")
    
    # Test error resolution
    error_suggestions = test_error_resolution()
    logger.info(f"Error resolution suggestions: {len(error_suggestions)}")
    for suggestion in error_suggestions:
        logger.info(f"- {suggestion.type.value}: {suggestion.description}")
    
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    main() 