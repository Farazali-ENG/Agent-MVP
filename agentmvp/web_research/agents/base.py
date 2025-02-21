from typing import List, Any
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseLanguageModel

class ResearchAgentBase(ABC):
    """Base class for research agents
    
    Each agent is responsible for:
    - Defining its own data structures
    - Implementing its own research approach
    - Managing its own persistence
    - Formatting its own output
    """
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self._setup()
    
    @abstractmethod
    def _setup(self):
        """Setup agent-specific components"""
        pass
    
    @abstractmethod
    async def research(self, queries: List[str]) -> Any:
        """Conduct research based on queries
        
        Args:
            queries: List of research queries to investigate
            
        Returns:
            Research results in agent-specific format
        """
        pass
        
    @abstractmethod
    def get_name(self) -> str:
        """Get agent identifier for coordination"""
        pass