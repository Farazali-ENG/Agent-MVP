"""
InsightIntegrator combines research insights into actionable sales strategies.
"""

from typing import Dict
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

class InsightIntegrator:
    """Integrates research insights into actionable sales strategies"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self._setup()
    
    def _setup(self) -> None:
        """Setup prompts for insight integration"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at integrating research insights into actionable sales strategies.
            
            Analyze the provided research to extract key insights that will help AI agents sell more effectively.
            Focus on practical applications of research in sales conversations.
            
            Structure your response in these sections:

            # Market Understanding
            ## Customer Profile
            - Key demographics
            - Decision drivers
            - Pain points
            - Success criteria
            
            ## Value Analysis
            - Core value propositions
            - Competitive advantages
            - Market positioning
            - Proof points
            
            ## Purchase Psychology
            - Decision patterns
            - Buying triggers
            - Risk factors
            - Trust elements

            # Sales Application
            ## Conversation Strategy
            [How to apply insights in sales talks]
            
            ## Value Communication
            [Ways to present value effectively]
            
            ## Trust Development
            [Methods to build credibility]

            # Competitive Edge
            ## Differentiation Points
            [Key advantages to emphasize]
            
            ## Objection Prevention
            [How to preempt concerns]
            
            ## Value Reinforcement
            [Ways to strengthen value perception]

            # Implementation Guide
            [Specific examples showing how to use these insights in sales]"""),
            ("human", """Integrate research insights from these components:
            
            Research Data:
            {research}""")
        ])
    
    async def analyze_content(self, research: Dict) -> Dict:
        """Analyze research for psychological insights"""
        try:
            messages = self.analysis_prompt.format_messages(
                research=research
            )
            response = await self.llm.ainvoke(messages)
            
            return {
                "insight_narrative": response.content,
                "components": {
                    "market_understanding": self._extract_section(response.content, "Market Understanding"),
                    "sales_application": self._extract_section(response.content, "Sales Application"),
                    "competitive_edge": self._extract_section(response.content, "Competitive Edge"),
                    "implementation_guide": self._extract_section(response.content, "Implementation Guide")
                }
            }
            
        except Exception as e:
            print(f"Error analyzing insights: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"insight_narrative": "Error generating insights"}

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from the content"""
        # Implementation to parse named sections from the content
        return ""
    
    async def research(self, query_data: Dict) -> Dict:
        """Research and integrate insights"""
        try:
            analysis_results = await self.analyze_content(query_data.get("research_data", {}))
            return analysis_results
            
        except Exception as e:
            print(f"Error researching insights: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"insight_narrative": "Error generating insights"} 