"""
Agent specialized in analyzing customer psychology and decision-making patterns.
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
    EmotionalLanguageAnalyzer,
    PersuasionPatternAnalyzer,
    CognitiveBiasAnalyzer,
    UserIntentAnalyzer
)
from ..base import ResearchAgentBase


class CustomerPsychologyAgent(ResearchAgentBase):
    """Agent specialized in analyzing customer psychology and decision-making patterns"""
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)
    
    def get_name(self) -> str:
        return "customer_psychology"
    
    def _setup(self) -> None:
        """Setup the agent with its tools and prompts"""
        # Initialize tools
        self.tools = [
            EmotionalLanguageAnalyzer(),
            PersuasionPatternAnalyzer(),
            CognitiveBiasAnalyzer(),
            UserIntentAnalyzer()
        ]
        
        # Setup analysis prompt
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing customer psychology and decision-making patterns.
            
            Analyze the provided company information to help AI sales agents understand and connect with customers effectively."""),
            
            ("human", """Company: {company_name}
            
            Website Summary:
            {website_content}
            
            Create a structured analysis of customer psychology to help AI sales agents engage effectively.""")
        ])
    
    async def _analyze_psychological_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze text using psychological analysis tools"""
        results = {}
        
        # Analyze using various tools
        results['emotional'] = await self.tools[0].arun(text)
        results['persuasion'] = await self.tools[1].arun(text)
        results['cognitive_bias'] = await self.tools[2].arun(text)
        results['intent'] = await self.tools[3].arun(text)
        
        return results
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze customer psychology based on website summary
        
        Args:
            queries: List containing:
                - First element: Company name
                - Second element: Website content summary
                
        Returns:
            Dict containing structured psychological analysis
        """
        if len(queries) < 2:
            raise ValueError("Need both company name and website content")
            
        company_name = queries[0]
        website_content = queries[1]
        
        # Analyze psychological patterns
        patterns = await self._analyze_psychological_patterns(website_content)
        
        # Format analysis input
        analysis_input = f"""
        Company: {company_name}
        
        Website Summary:
        {website_content}
        
        Psychological Analysis:
        
        Emotional Patterns:
        {patterns['emotional']}
        
        Persuasion Elements:
        {patterns['persuasion']}
        
        Cognitive Biases:
        {patterns['cognitive_bias']}
        
        User Intent:
        {patterns['intent']}
        """
        
        # Generate analysis
        messages = self.analysis_prompt.format_messages(
            company_name=company_name,
            website_content=analysis_input
        )
        response = await self.llm.ainvoke(messages)
        
        # Extract sections
        content = response.content
        return {
            "narrative": content,
            "components": {
                "psychological_profile": self._extract_section(content, "Psychological Profile"),
                "decision_framework": self._extract_section(content, "Decision Framework"),
                "trust_building": self._extract_section(content, "Trust Building"),
                "communication": self._extract_section(content, "Communication Guide"),
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