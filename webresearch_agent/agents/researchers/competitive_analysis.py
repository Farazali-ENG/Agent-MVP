from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import asyncio
import json

from ...tools.psychological import (
    MarketAnalyzer,
    CompetitorAnalyzer,
    PositioningAnalyzer,
    TrendAnalyzer,
    WebSearchTool
)

from ..base import ResearchAgentBase
from ..shared import ResearchNarrative, format_narrative_as_markdown


class CompetitiveAnalysisResponse(BaseModel):
    market_position: List[str] = Field(description="Current market positioning and standing")
    competitive_advantages: List[str] = Field(description="Key competitive advantages identified")
    competitor_strategies: List[str] = Field(description="Notable competitor strategies and approaches")
    market_trends: List[str] = Field(description="Relevant market trends and developments")
    growth_opportunities: List[str] = Field(description="Potential areas for growth and expansion")
    threat_assessment: List[str] = Field(description="Identified market threats and challenges")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "market_position": ["Market leader in X", "Strong regional presence"],
                    "competitive_advantages": ["Superior technology", "Better service"],
                    "competitor_strategies": ["Price competition", "Market expansion"],
                    "market_trends": ["Industry digitalization", "Sustainability focus"],
                    "growth_opportunities": ["New market segments", "Product expansion"],
                    "threat_assessment": ["New competitors", "Changing regulations"]
                }
            ]
        }
    }

class CompetitiveSynthesis(BaseModel):
    market_landscape: Dict[str, List[str]] = Field(
        description="Analysis of market position and competitive dynamics",
        default_factory=lambda: {
            "strengths": [],
            "weaknesses": [],
            "opportunities": [],
            "threats": []
        }
    )
    competitive_strategy: Dict[str, List[str]] = Field(
        description="Strategic recommendations for competitive positioning",
        default_factory=lambda: {
            "differentiation_points": [],
            "market_opportunities": [],
            "defensive_strategies": []
        }
    )
    trend_implications: Dict[str, List[str]] = Field(
        description="Impact of market trends on strategy",
        default_factory=lambda: {
            "short_term_actions": [],
            "long_term_planning": [],
            "risk_mitigation": []
        }
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "market_landscape": {
                        "strengths": ["Market leadership", "Strong brand"],
                        "weaknesses": ["Limited reach", "Resource constraints"],
                        "opportunities": ["Market gaps", "New technologies"],
                        "threats": ["Competitive pressure", "Market changes"]
                    },
                    "competitive_strategy": {
                        "differentiation_points": ["Unique features", "Service quality"],
                        "market_opportunities": ["Growth areas", "New segments"],
                        "defensive_strategies": ["Market protection", "Customer retention"]
                    },
                    "trend_implications": {
                        "short_term_actions": ["Quick wins", "Immediate response"],
                        "long_term_planning": ["Strategic initiatives", "Future positioning"],
                        "risk_mitigation": ["Risk management", "Contingency plans"]
                    }
                }
            ]
        }
    }

class CompetitiveAnalysisAgent(ResearchAgentBase):
    """Agent specialized in analyzing competitive landscape and market positioning"""
    
    def __init__(self, llm: BaseLanguageModel):
        tools = [
            MarketAnalyzer(),
            PositioningAnalyzer(),
            WebSearchTool()
        ]
        
        role_description = "competitive landscape and market positioning"
        narrative_focus = """
        how the company positions itself in the market and differentiates from competitors.
        Focus on understanding competitive advantages, market dynamics, positioning strategy,
        and unique value drivers. Explain how these factors influence customer choice and loyalty.
        """
        
        super().__init__(llm, tools, role_description, narrative_focus)
    
    async def _analyze_competitive_position(self, text: str) -> Dict[str, Any]:
        """Analyze text for competitive positioning insights"""
        results = {}
        
        # Analyze market dynamics
        market_results = await self.tools[0].arun(text)
        results['market_dynamics'] = market_results
        
        # Analyze positioning strategy
        positioning_results = await self.tools[1].arun(text)
        results['positioning_strategy'] = positioning_results
        
        # Gather additional competitive context if needed
        if len(text.split()) < 100:  # If input text is short, gather more context
            search_results = await self.tools[2].arun(text)
            results['competitive_context'] = search_results
        
        return results
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """
        Conduct competitive analysis based on queries.
        
        Args:
            queries: List of research queries to investigate
            
        Returns:
            Dict containing research results in narrative format
        """
        narratives = []
        
        for query in queries:
            try:
                # Analyze competitive position
                analysis_results = await self._analyze_competitive_position(query)
                
                # Create comprehensive input for narrative generation
                analysis_text = f"""
                Research Query: {query}
                
                Market Dynamics Analysis:
                {analysis_results['market_dynamics']}
                
                Positioning Strategy:
                {analysis_results['positioning_strategy']}
                
                Competitive Context:
                {analysis_results.get('competitive_context', 'No additional context needed.')}
                """
                
                # Generate narrative from analysis
                narrative = await self._analyze_content(analysis_text)
                narratives.append(narrative)
                
            except Exception as e:
                print(f"Error analyzing query '{query}': {str(e)}")
                continue
        
        try:
            # Synthesize all narratives into a cohesive story
            if narratives:
                final_narrative = await self._synthesize_narratives(narratives)
                
                # Format results as Markdown
                markdown_output = format_narrative_as_markdown(
                    final_narrative,
                    "Competitive Analysis"
                )
                
                return {
                    "narrative": final_narrative.model_dump(),
                    "markdown": markdown_output
                }
            else:
                raise ValueError("No successful analyses to synthesize")
                
        except Exception as e:
            print(f"Error synthesizing narratives: {str(e)}")
            raise 