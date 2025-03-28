from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import asyncio
import json

from agents.web_research.tools.psychological import (
    SentimentAnalyzer,
    TrendAnalyzer,
    ImpactAnalyzer,
    WebSearchTool,
    EmotionalLanguageAnalyzer
)

from agents.web_research.agents.base import NarrativeResearchAgent
from agents.web_research.agents.shared import ResearchNarrative, format_narrative_as_markdown

class NewsAnalysisResponse(BaseModel):
    """Response model for news analysis"""
    sentiment_indicators: List[str] = Field(description="Key sentiment indicators from news coverage")
    trend_patterns: List[str] = Field(description="Identified trends and patterns in news")
    impact_factors: List[str] = Field(description="Factors indicating news impact and significance")
    coverage_themes: List[str] = Field(description="Major themes in news coverage")
    reputation_signals: List[str] = Field(description="Signals affecting company reputation")
    market_implications: List[str] = Field(description="Market and industry implications")

class NewsSynthesis(BaseModel):
    """Synthesis model for news analysis insights"""
    sentiment_analysis: Dict[str, List[str]] = Field(
        description="Analysis of sentiment patterns in news coverage",
        default_factory=lambda: {
            "positive_signals": [],
            "negative_signals": [],
            "neutral_signals": []
        }
    )
    trend_implications: Dict[str, List[str]] = Field(
        description="Implications of identified trends",
        default_factory=lambda: {
            "market_trends": [],
            "industry_changes": [],
            "growth_indicators": []
        }
    )
    strategic_considerations: Dict[str, List[str]] = Field(
        description="Strategic considerations based on news analysis",
        default_factory=lambda: {
            "opportunities": [],
            "challenges": [],
            "action_items": []
        }
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sentiment_analysis": {
                        "positive_signals": ["Strong market reception", "Customer satisfaction"],
                        "negative_signals": ["Industry challenges", "Market concerns"],
                        "neutral_signals": ["Regulatory changes", "Market shifts"]
                    },
                    "trend_implications": {
                        "market_trends": ["Growing demand", "Shifting preferences"],
                        "industry_changes": ["Technology adoption", "New regulations"],
                        "growth_indicators": ["Market expansion", "Innovation focus"]
                    },
                    "strategic_considerations": {
                        "opportunities": ["Market gaps", "Partnership potential"],
                        "challenges": ["Competition", "Resource constraints"],
                        "action_items": ["Strategic initiatives", "Risk mitigation"]
                    }
                }
            ]
        }
    }

class NewsAnalysisAgent(NarrativeResearchAgent):
    """Agent specialized in analyzing news coverage and market perception"""
    
    def __init__(self, llm: BaseLanguageModel):
        tools = [
            EmotionalLanguageAnalyzer(),
            TrendAnalyzer(),
            WebSearchTool()
        ]
        
        role_description = "news coverage and market perception"
        narrative_focus = """
        how the company is perceived in news coverage and market discussions.
        Focus on understanding media sentiment, industry trends, public perception,
        and market positioning. Explain how these factors shape the company's image
        and influence customer confidence.
        """
        
        super().__init__(llm, tools, role_description, narrative_focus)
    
    async def _analyze_news_coverage(self, text: str) -> Dict[str, Any]:
        """Analyze text for news and market perception insights"""
        results = {}
        
        # Analyze emotional sentiment in coverage
        sentiment_results = await self.tools[0].arun(text)
        results['media_sentiment'] = sentiment_results
        
        # Analyze market trends
        trend_results = await self.tools[1].arun(text)
        results['market_trends'] = trend_results
        
        # Gather additional news context if needed
        if len(text.split()) < 100:  # If input text is short, gather more context
            search_results = await self.tools[2].arun(text)
            results['news_context'] = search_results
        
        return results
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """
        Conduct news and perception analysis based on queries.
        
        Args:
            queries: List of research queries to investigate
            
        Returns:
            Dict containing research results in narrative format
        """
        narratives = []
        
        for query in queries:
            try:
                # Analyze news coverage
                analysis_results = await self._analyze_news_coverage(query)
                
                # Create comprehensive input for narrative generation
                analysis_text = f"""
                Research Query: {query}
                
                Media Sentiment Analysis:
                {analysis_results['media_sentiment']}
                
                Market Trends:
                {analysis_results['market_trends']}
                
                News Context:
                {analysis_results.get('news_context', 'No additional context needed.')}
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
                    "News and Market Perception Analysis"
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