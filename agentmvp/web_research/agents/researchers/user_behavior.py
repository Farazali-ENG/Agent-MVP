"""
Agent specialized in analyzing user behavior patterns and engagement preferences.
"""

from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from ...tools.psychological import (
    MarketAnalyzer,
    CompetitorAnalyzer,
    PositioningAnalyzer,
    TrendAnalyzer,
    WebSearchTool,
    UserIntentAnalyzer,
    SocialInfluenceAnalyzer,
    TrustSignalAnalyzer
)
from ..base import ResearchAgentBase

class UserBehaviorAgent(ResearchAgentBase):
    """Agent specialized in analyzing user behavior and decision patterns"""
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)
    
    def get_name(self) -> str:
        return "user_behavior"
    
    def _setup(self) -> None:
        """Setup the agent with its prompts"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at understanding user behavior, engagement patterns, and interaction preferences.
            
            Analyze the provided company information and create a structured analysis that helps AI sales agents understand:
            
            1. Discovery Behavior
            - How do users find and evaluate solutions?
            - What information sources do they trust?
            - What research patterns do they follow?
            - What triggers initial interest?
            
            2. Engagement Patterns
            - How do they prefer to interact?
            - What communication channels work best?
            - What content formats resonate most?
            - What engagement style do they respond to?
            
            3. Decision Journey
            - What steps do they take before buying?
            - What information do they need when?
            - What validation do they seek?
            - What accelerates or delays decisions?
            
            4. Success Indicators
            - What signals show buying intent?
            - How do they express interest?
            - What shows they're ready to commit?
            - What indicates resistance?
            
            Structure your response in these sections:

            # Discovery Analysis
            ## Search Patterns
            [How users find and research solutions]
            
            ## Information Needs
            [Critical information for decision-making]
            
            ## Trust Signals
            [What builds credibility during research]

            # Engagement Framework
            ## Channel Preferences
            [Preferred communication methods]
            
            ## Content Preferences
            [Most effective content types]
            
            ## Interaction Style
            [How they like to engage]

            # Journey Mapping
            ## Decision Steps
            [Key stages in buying process]
            
            ## Information Flow
            [What information is needed when]
            
            ## Validation Points
            [How they verify and validate]

            # Conversion Signals
            ## Interest Indicators
            [Signs of genuine interest]
            
            ## Readiness Signals
            [Indicators of purchase readiness]
            
            ## Resistance Patterns
            [Signs of hesitation or concern]

            # Sales Guidance
            [Specific tactics for engaging effectively]"""),
            ("human", """Company: {company_name}
            
            Website Summary:
            {website_content}
            
            Create a structured analysis of user behavior to help AI sales agents engage effectively.""")
        ])
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze user behavior based on website summary
        
        Args:
            queries: List containing:
                - First element: Company name
                - Second element: Website content summary
                
        Returns:
            Dict containing structured behavior analysis
        """
        if len(queries) < 2:
            raise ValueError("Need both company name and website content")
            
        company_name = queries[0]
        website_content = queries[1]
        
        # Generate analysis
        messages = self.analysis_prompt.format_messages(
            company_name=company_name,
            website_content=website_content
        )
        response = await self.llm.ainvoke(messages)
        
        # Extract sections
        content = response.content
        return {
            "narrative": content,
            "components": {
                "discovery": self._extract_section(content, "Discovery Analysis"),
                "engagement": self._extract_section(content, "Engagement Framework"),
                "journey": self._extract_section(content, "Journey Mapping"),
                "conversion": self._extract_section(content, "Conversion Signals"),
                "sales_guidance": self._extract_section(content, "Sales Guidance")
            }
        }
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from the analysis content"""
        try:
            start = content.index(f"# {section_name}")
            next_section = content.find("\n# ", start + 1)
            if next_section == -1:
                return content[start:].strip()
            return content[start:next_section].strip()
        except ValueError:
            return "" 