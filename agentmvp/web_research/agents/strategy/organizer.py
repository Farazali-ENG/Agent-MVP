"""
TacticOrganizer structures sales tactics and techniques from research insights.
"""

from typing import Dict
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

class TacticOrganizer:
    """Organizes sales tactics and techniques from research"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self._setup()
    
    def _setup(self) -> None:
        """Setup prompts for tactics organization"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at organizing sales tactics and techniques from research insights.
            
            Analyze the provided research to create a tactical sales framework that helps AI agents convert prospects.
            Focus on practical selling approaches that leverage psychology and value propositions effectively.
            
            Structure your response in these sections:

            # Engagement Tactics
            ## Initial Contact
            - First impression techniques
            - Interest generation approaches
            - Trust foundation methods
            - Qualification strategies
            
            ## Value Demonstration
            - Value proposition delivery
            - Pain point alignment
            - Benefit reinforcement
            - Proof point usage
            
            ## Objection Handling
            - Prevention techniques
            - Response frameworks
            - Confidence building
            - Risk mitigation
            
            ## Closing Techniques
            - Readiness assessment
            - Decision facilitation
            - Commitment securing
            - Follow-through methods

            # Psychological Tools
            ## Influence Patterns
            [Key psychological techniques for persuasion]
            
            ## Trust Building
            [Tactical approaches to building sales trust]
            
            ## Decision Triggers
            [Ways to activate buying decisions]

            # Conversation Control
            ## Pacing Techniques
            [How to control conversation flow]
            
            ## Redirection Methods
            [Ways to maintain sales focus]
            
            ## Advancement Signals
            [Signs to progress the sale]

            # Tactical Examples
            [Specific scenarios showing these sales tactics in action]"""),
            ("human", """Organize sales tactics based on this research:
            
            Research Data:
            {research}""")
        ])
    
    async def analyze_content(self, research: Dict) -> Dict:
        """Analyze research for tactical elements"""
        try:
            messages = self.analysis_prompt.format_messages(
                research=research
            )
            response = await self.llm.ainvoke(messages)
            
            return {
                "tactics_narrative": response.content,
                "components": {
                    "engagement_tactics": self._extract_section(response.content, "Engagement Tactics"),
                    "psychological_tools": self._extract_section(response.content, "Psychological Tools"),
                    "conversation_control": self._extract_section(response.content, "Conversation Control"),
                    "tactical_examples": self._extract_section(response.content, "Tactical Examples")
                }
            }
            
        except Exception as e:
            print(f"Error analyzing tactics: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"tactics_narrative": "Error generating tactics"}

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from the content"""
        # Implementation to parse named sections from the content
        return ""
    
    async def research(self, query_data: Dict) -> Dict:
        """Research and organize tactics"""
        try:
            analysis_results = await self.analyze_content(query_data.get("research_data", {}))
            return analysis_results
            
        except Exception as e:
            print(f"Error researching tactics: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"tactics_narrative": "Error generating tactics"} 