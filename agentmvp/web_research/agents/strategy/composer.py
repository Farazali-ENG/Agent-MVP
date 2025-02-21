"""
StrategyComposer integrates insights and tactics into psychologically-aware conversation strategies.
"""

from typing import Dict
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

class StrategyComposer:
    """Composes psychologically-informed conversation strategies"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self._setup()
    
    def _setup(self) -> None:
        """Setup prompts for strategy composition"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating persuasive sales conversation strategies from research insights.
            
            Analyze the provided insights and tactics to create a comprehensive sales conversation framework that:
            1. Leverages psychological understanding to influence decisions
            2. Uses value propositions effectively in conversations
            3. Builds trust through strategic communication
            4. Guides prospects naturally toward commitment
            
            Structure your response in these sections:

            # Sales Psychology Framework
            ## Customer Mindset
            [Analysis of customer psychology and decision drivers]
            
            ## Value Triggers
            [Key psychological triggers that connect with value props]
            
            ## Trust Elements
            [Critical factors for building sales trust]

            # Sales Conversation Architecture
            ## Opening Techniques
            [Effective ways to start sales conversations]
            
            ## Value Presentation
            [How to present value props persuasively]
            
            ## Objection Management
            [Psychological techniques for handling concerns]

            # Sales Intelligence Guide
            ## Buying Signals
            [How to read prospect psychology and interest]
            
            ## Adaptation Rules
            [When and how to adjust sales approach]
            
            ## Closing Patterns
            [Psychological techniques for gaining commitment]

            # Implementation Examples
            [Detailed sales conversation scenarios showing techniques in action]"""),
            ("human", """Create a sales conversation strategy based on these research insights:
            
            Customer Research:
            {insights}
            
            Sales Approaches:
            {tactics}""")
        ])
    
    async def analyze_content(self, insights: Dict, tactics: Dict) -> Dict:
        """Analyze insights and tactics for psychological strategy elements"""
        try:
            messages = self.analysis_prompt.format_messages(
                insights=insights,
                tactics=tactics
            )
            response = await self.llm.ainvoke(messages)
            
            return {
                "strategy_narrative": response.content,
                "components": {
                    "psychological_framework": self._extract_section(response.content, "Psychological Framework"),
                    "conversation_architecture": self._extract_section(response.content, "Conversation Architecture"),
                    "emotional_intelligence": self._extract_section(response.content, "Emotional Intelligence Guide"),
                    "examples": self._extract_section(response.content, "Implementation Examples")
                }
            }
            
        except Exception as e:
            print(f"Error analyzing strategy content: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"strategy_narrative": "Error generating strategy"}

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from the strategy content"""
        # Implementation to parse named sections from the content
        return ""
    
    async def research(self, query_data: Dict) -> Dict:
        """Research and compose strategy based on query data"""
        try:
            insights = query_data.get('insights', {})
            tactics = query_data.get('tactics', {})
            
            analysis_results = await self.analyze_content(insights, tactics)
            
            return analysis_results
            
        except Exception as e:
            print(f"Error researching strategy: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"strategy_narrative": "Error generating strategy"} 