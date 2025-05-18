from typing import Any, Dict, Optional
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.llms.base import BaseLLM

from .base import BaseMCP, MCPConfig

class LLMPromptConfig(MCPConfig):
    """Configuration for LLM Prompt MCP"""
    model_provider: str = "openai"
    model_name: str = "gpt-3.5-turbo"
    prompt_template: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class LLMPromptMCP(BaseMCP):
    """MCP for executing LLM prompts"""
    
    def __init__(self, config: LLMPromptConfig):
        super().__init__(config)
        self.llm = self._get_llm()
        self.prompt_template = PromptTemplate(
            template=config.prompt_template,
            input_variables=self._extract_input_variables(config.prompt_template)
        )
    
    def _get_llm(self) -> BaseLLM:
        """Get the configured LLM instance"""
        if self.config.model_provider == "openai":
            return ChatOpenAI(
                model_name=self.config.model_name,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
        else:
            raise ValueError(f"Unsupported model provider: {self.config.model_provider}")
    
    def _extract_input_variables(self, template: str) -> list[str]:
        """Extract input variables from prompt template"""
        # Simple implementation - could be enhanced with proper parsing
        import re
        return list(set(re.findall(r'\{([^}]+)\}', template)))
    
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the LLM prompt with given inputs
        
        Args:
            inputs: Dictionary of input parameters for the prompt template
            
        Returns:
            Dictionary containing the LLM response
        """
        # Format prompt with inputs
        formatted_prompt = self.prompt_template.format(**inputs)
        
        # Execute against LLM
        response = await self.llm.agenerate([formatted_prompt])
        
        return {
            "result": response.generations[0][0].text,
            "model": self.config.model_name,
            "prompt": formatted_prompt
        } 