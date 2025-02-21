"""
Agent specialized in analyzing company value propositions and competitive differentiation.
"""

from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from ...tools.psychological import (
    MarketAnalyzer,
    CompetitorAnalyzer,
    PositioningAnalyzer,
    TrendAnalyzer,
    WebSearchTool
)
from ..base import ResearchAgentBase

class ValuePropositionAgent(ResearchAgentBase):
    """Agent specialized in analyzing company value propositions"""
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)
    
    def get_name(self) -> str:
        return "value_proposition"
    
    def _setup(self) -> None:
        """Setup the agent with its prompts"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing value propositions and competitive differentiation.
            
            Analyze the provided company information and create a structured analysis that helps AI sales agents understand:
            
            1. Core Value Propositions
            - What are the key benefits and outcomes offered?
            - How do these translate to customer value?
            - What makes these benefits meaningful?
            - What evidence supports these claims?
            
            2. Competitive Differentiation
            - What makes this solution unique?
            - How does it compare to alternatives?
            - What specific advantages stand out?
            - Where does it excel vs competitors?
            
            3. Value Triggers
            - What situations make value most apparent?
            - Which customer types see highest value?
            - What metrics demonstrate value best?
            - What proof points are most compelling?
            
            4. Value Communication
            - How should benefits be presented?
            - What analogies or frameworks work best?
            - How to quantify value and ROI?
            - What stories illustrate value best?
            
            Structure your response in these sections:

            # Value Framework
            ## Core Benefits
            [List and describe key value propositions]
            
            ## Value Metrics
            [Quantifiable outcomes and ROI measures]
            
            ## Success Criteria
            [How customers measure and validate value]

            # Competitive Edge
            ## Key Differentiators
            [Unique advantages and capabilities]
            
            ## Market Position
            [How solution stands out in market]
            
            ## Win Factors
            [Why customers choose this solution]

            # Value Triggers
            ## Activation Points
            [When value becomes most apparent]
            
            ## Customer Segments
            [Who sees most value and why]
            
            ## Proof Points
            [Evidence that validates value claims]

            # Communication Framework
            ## Value Stories
            [Narratives that illustrate benefits]
            
            ## ROI Model
            [How to demonstrate financial value]
            
            ## Presentation Flow
            [How to sequence value messages]

            # Sales Guidance
            [Specific tactics for communicating value]"""),
            ("human", """Company: {company_name}
            
            Website Summary:
            {website_content}
            
            Create a structured analysis of value propositions and differentiation to help AI sales agents communicate value effectively.""")
        ])
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze company value proposition based on website summary
        
        Args:
            queries: List containing:
                - First element: Company name
                - Second element: Website content summary
                
        Returns:
            Dict containing structured value proposition analysis
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
                "value_framework": self._extract_section(content, "Value Framework"),
                "competitive_edge": self._extract_section(content, "Competitive Edge"),
                "value_triggers": self._extract_section(content, "Value Triggers"),
                "communication": self._extract_section(content, "Communication Framework"),
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