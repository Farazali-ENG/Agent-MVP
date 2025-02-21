"""
Agent specialized in identifying and analyzing customer pain points and objection patterns.
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

class PainPointsAgent(ResearchAgentBase):
    """Agent specialized in identifying and analyzing customer pain points"""
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)
    
    def get_name(self) -> str:
        return "pain_points"
    
    def _setup(self) -> None:
        """Setup the agent with its prompts"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at understanding customer pain points, objection patterns, and solution gaps.
            
            Analyze the provided company information and create a structured analysis that helps AI sales agents understand:
            
            1. Core Pain Points
            - What specific problems and challenges do customers face?
            - How do these issues impact their daily lives or operations?
            - What are the emotional and practical costs of these problems?
            - How urgent or severe are these challenges?
            
            2. Solution Landscape
            - What solutions have they tried before?
            - Why haven't previous solutions worked?
            - What makes existing solutions inadequate?
            - What specific gaps remain unfilled?
            
            3. Objection Patterns
            - What common objections arise during sales?
            - What underlying concerns drive these objections?
            - How do competitors typically fail to address these?
            - What proof points are needed to overcome objections?
            
            4. Value Alignment
            - How do pain points map to specific value props?
            - What ROI metrics matter most for each pain?
            - Which benefits resonate most emotionally?
            - What validation do prospects need?
            
            Structure your response in these sections:

            # Pain Point Analysis
            ## Core Challenges
            [List and describe key pain points with severity and impact]
            
            ## Emotional Impact
            [How these challenges affect customers emotionally]
            
            ## Business Impact
            [Quantifiable effects on operations or outcomes]

            # Solution Gaps
            ## Current Solutions
            [Analysis of existing solution attempts]
            
            ## Unmet Needs
            [Specific aspects still needing better solutions]
            
            ## Competitive Gaps
            [How competitors fail to fully address needs]

            # Objection Framework
            ## Common Objections
            [List and analyze typical sales objections]
            
            ## Underlying Concerns
            [Root causes and emotional drivers of objections]
            
            ## Validation Needs
            [Proof points needed to overcome each objection]

            # Value Alignment
            ## Pain-Value Mapping
            [How specific pains map to value propositions]
            
            ## ROI Drivers
            [Key metrics and outcomes prospects care about]
            
            ## Trust Triggers
            [What builds confidence in the solution]

            # Sales Guidance
            [Specific tactics for addressing pains and objections]"""),
            ("human", """Company: {company_name}
            
            Website Summary:
            {website_content}
            
            Create a structured analysis of customer pain points, objections, and value alignment to help AI sales agents engage effectively.""")
        ])
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze customer pain points based on website summary
        
        Args:
            queries: List containing:
                - First element: Company name
                - Second element: Website content summary
                
        Returns:
            Dict containing structured pain point analysis
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
                "pain_points": self._extract_section(content, "Pain Point Analysis"),
                "solution_gaps": self._extract_section(content, "Solution Gaps"),
                "objections": self._extract_section(content, "Objection Framework"),
                "value_alignment": self._extract_section(content, "Value Alignment"),
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