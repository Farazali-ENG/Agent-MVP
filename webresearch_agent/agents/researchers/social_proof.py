from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser
import asyncio
import json

from agents.web_research.tools.psychological import (
    SocialInfluenceAnalyzer,
    TrustSignalAnalyzer,
    EmotionalLanguageAnalyzer,
    WebSearchTool,
    PersuasionPatternAnalyzer
)

from agents.web_research.agents.base import NarrativeResearchAgent
from agents.web_research.agents.shared import ResearchNarrative, format_narrative_as_markdown

class SocialProofResponse(BaseModel):
    testimonials: List[str] = Field(description="Key customer testimonials and reviews")
    case_studies: List[str] = Field(description="Notable case studies and success stories")
    credentials: List[str] = Field(description="Professional credentials and certifications")
    social_signals: List[str] = Field(description="Social media presence and engagement")
    trust_indicators: List[str] = Field(description="Trust-building elements and proof")
    authority_markers: List[str] = Field(description="Industry authority and leadership indicators")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "testimonials": ["Great service!", "Highly recommended"],
                    "case_studies": ["Success story with Client A", "Project B results"],
                    "credentials": ["Industry certified", "Award winning"],
                    "social_signals": ["10k followers", "Active community"],
                    "trust_indicators": ["5-star rating", "BBB accredited"],
                    "authority_markers": ["Industry leader", "Expert team"]
                }
            ]
        }
    }

class SocialProofSynthesis(BaseModel):
    credibility_elements: Dict[str, List[str]] = Field(
        description="Elements that establish credibility and trust",
        default_factory=lambda: {
            "customer_validation": [],
            "professional_authority": [],
            "social_validation": []
        }
    )
    trust_framework: Dict[str, List[str]] = Field(
        description="Framework for building and maintaining trust",
        default_factory=lambda: {
            "proof_points": [],
            "trust_signals": [],
            "credibility_markers": []
        }
    )
    engagement_patterns: Dict[str, List[str]] = Field(
        description="Patterns of social engagement and influence",
        default_factory=lambda: {
            "community_engagement": [],
            "social_impact": [],
            "relationship_building": []
        }
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "credibility_elements": {
                        "customer_validation": ["Positive reviews", "Testimonials"],
                        "professional_authority": ["Certifications", "Awards"],
                        "social_validation": ["Social media presence", "Community engagement"]
                    },
                    "trust_framework": {
                        "proof_points": ["Case studies", "Results"],
                        "trust_signals": ["Guarantees", "Transparency"],
                        "credibility_markers": ["Experience", "Expertise"]
                    },
                    "engagement_patterns": {
                        "community_engagement": ["Active responses", "Community events"],
                        "social_impact": ["Charitable work", "Community support"],
                        "relationship_building": ["Long-term partnerships", "Client retention"]
                    }
                }
            ]
        }
    }

class SocialProofAgent(NarrativeResearchAgent):
    """Agent specialized in analyzing social proof and trust signals"""
    
    def __init__(self, llm: BaseLanguageModel):
        tools = [
            EmotionalLanguageAnalyzer(),
            PersuasionPatternAnalyzer(),
            WebSearchTool()
        ]
        
        role_description = "social proof and trust-building elements"
        narrative_focus = """
        how social proof, testimonials, and trust signals influence customer confidence and decisions.
        Focus on understanding the impact of different types of social validation, credibility markers,
        and trust-building elements. Explain how these factors shape customer perception and trust.
        """
        
        super().__init__(llm, tools, role_description, narrative_focus)
    
    async def _analyze_social_proof(self, text: str) -> Dict[str, Any]:
        """Analyze text for social proof elements"""
        results = {}
        
        # Analyze emotional impact of social proof
        emotional_results = await self.tools[0].arun(text)
        results['emotional_impact'] = emotional_results
        
        # Analyze persuasion patterns in testimonials
        persuasion_results = await self.tools[1].arun(text)
        results['persuasion_elements'] = persuasion_results
        
        # Gather additional social proof if needed
        if len(text.split()) < 100:  # If input text is short, gather more context
            search_results = await self.tools[2].arun(text)
            results['social_context'] = search_results
        
        return results
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """
        Conduct social proof research based on queries.
        
        Args:
            queries: List of research queries to investigate
            
        Returns:
            Dict containing research results in narrative format
        """
        narratives = []
        
        for query in queries:
            try:
                # Analyze social proof elements
                analysis_results = await self._analyze_social_proof(query)
                
                # Create comprehensive input for narrative generation
                analysis_text = f"""
                Research Query: {query}
                
                Emotional Impact Analysis:
                {analysis_results['emotional_impact']}
                
                Persuasion Elements:
                {analysis_results['persuasion_elements']}
                
                Social Context:
                {analysis_results.get('social_context', 'No additional context needed.')}
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
                    "Social Proof Analysis"
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