"""
SalesStrategyBuilder coordinates the building of comprehensive sales strategies.
"""

from typing import Dict, List, Any
import asyncio
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

from .composer import StrategyComposer
from .organizer import TacticOrganizer
from .integrator import InsightIntegrator
from .conversation_starters import ConversationStarterAgent

class SalesStrategyBuilder:
    """Builds comprehensive sales strategies from research insights"""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize strategy builder components"""
        self.llm = llm
        self.integrator = InsightIntegrator(llm)
        self.organizer = TacticOrganizer(llm)
        self.composer = StrategyComposer(llm)
        self.starter_agent = ConversationStarterAgent(llm)
        self._setup()

    def _setup(self) -> None:
        """Setup the builder with its prompts"""
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at creating psychological sales strategies from research insights.
            
            Using the provided research components (customer psychology, value propositions, pain points, and user behavior),
            create a comprehensive sales strategy that will guide an AI agent through persuasive, psychologically-informed sales conversations.
            
            Structure your response in these sections:

            # Executive Summary
            [Key strategic elements for selling this specific product/service]

            # Sales Psychology Framework
            ## Target Customer Analysis
            [Synthesize research insights about customer psychology, pain points, and behavior]
            
            ## Value-Psychology Alignment
            [Map discovered value propositions to psychological needs and pain points]
            
            ## Trust-Building Strategy
            [Based on research insights about customer concerns and decision patterns]

            # Sales Conversation Architecture
            ## Understanding Phase
            - How to open conversations effectively
            - Initial trust-building approaches
            - Questions to uncover specific needs
            - Example dialogues showing this phase
            
            ## Value Presentation Phase
            - How to present value propositions persuasively
            - Psychological triggers to leverage
            - Objection prevention techniques
            - Example dialogues showing this phase
            
            ## Trust Deepening Phase
            - How to reinforce value alignment
            - Emotional connection techniques
            - Confidence building approaches
            - Example dialogues showing this phase
            
            ## Commitment Phase
            - Signs of readiness to commit
            - How to guide natural decisions
            - Risk mitigation techniques
            - Example dialogues showing this phase

            # Response Crafting Guide
            ## Tone and Style
            [Detailed guidance on communication tone, style, and emotional elements]
            
            ## Adaptation Framework
            [How to adapt communication based on customer states and conversation phases]
            
            ## Persuasion Patterns
            [Key psychological techniques and trust-building approaches]

            # Implementation Guide
            ## Key Principles
            [Core principles for implementing the strategy]
            
            ## Success Metrics
            [How to measure conversation effectiveness]
            
            ## Common Scenarios
            [Specific examples of handling typical situations]"""),
            ("human", """Create a comprehensive sales strategy by synthesizing these research components:
            
            Customer Psychology Insights:
            {insights}
            
            Sales Tactics Analysis:
            {tactics}
            
            Strategic Framework:
            {strategy}
            """)
        ])

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from the strategy content"""
        try:
            start = content.index(f"# {section_name}")
            next_section = content.find("\n# ", start + 1)
            if next_section == -1:
                return content[start:].strip()
            return content[start:next_section].strip()
        except ValueError:
            return ""
            
    async def build_strategy(self, research_results: Dict) -> Dict[str, Any]:
        """Build sales strategy from research results
        
        Args:
            research_results: Dict containing research components
            
        Returns:
            Dict containing final strategy and components
        """
        try:
            # Integrate research insights
            insights = await self.integrator.research({
                "research_data": research_results
            })
            
            # Organize sales tactics
            tactics = await self.organizer.research({
                "research_data": research_results
            })
            
            # Compose final strategy
            strategy = await self.composer.research({
                "insights": insights,
                "tactics": tactics
            })
            
            # Generate conversation starters
            conversation_starters = await self.starter_agent.research({
                "research_data": research_results
            })
            
            # Generate final synthesis
            messages = self.synthesis_prompt.format_messages(
                insights=insights.get("insight_narrative", ""),
                tactics=tactics.get("tactics_narrative", ""),
                strategy=strategy.get("strategy_narrative", "")
            )
            response = await self.llm.ainvoke(messages)
            content = response.content
            
            return {
                "final_strategy": content,
                "components": {
                    "executive_summary": self._extract_section(content, "Executive Summary"),
                    "psychology_framework": self._extract_section(content, "Sales Psychology Framework"),
                    "conversation_architecture": self._extract_section(content, "Sales Conversation Architecture"),
                    "response_guide": self._extract_section(content, "Response Crafting Guide"),
                    "conversation_starters": conversation_starters.get("conversation_starters", ""),
                    "implementation": self._extract_section(content, "Implementation Guide")
                }
            }
            
        except Exception as e:
            print(f"Error building strategy: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"final_strategy": "Error generating strategy"}

    def _extract_state_guide(self, content: str, state_name: str) -> Dict:
        """Extract guidance for a specific conversation state"""
        # Implementation to parse state-specific guidance from the content
        return {}

    def _get_error_response(self) -> Dict:
        """Get error response structure"""
        return {
            "final_strategy": "Error generating strategy",
            "components": {
                "psychological_insights": "",
                "conversation_tactics": "",
                "engagement_strategy": "",
                "state_guides": {
                    "understanding": {},
                    "value_presentation": {},
                    "trust_building": {},
                    "guidance": {}
                },
                "emotional_journey": "",
                "response_guide": ""
            }
        }

    def _get_default_strategy(self) -> Dict:
        """Get default strategy structure with basic content"""
        return {
            'tactics': {
                'key_points': [
                    'Build trust through expertise',
                    'Focus on value delivery',
                    'Address concerns proactively'
                ],
                'timing_recommendations': [
                    'Early engagement',
                    'Follow up within 24 hours',
                    'Regular check-ins'
                ],
                'approach_style': 'consultative',
                'effectiveness_metrics': {
                    'signals': ['engagement level', 'question frequency', 'objection types'],
                    'thresholds': ['response time < 24h', 'positive sentiment > 70%']
                }
            },
            'objection_handling': {
                'common_objections': [
                    'Cost concerns',
                    'Implementation timeline',
                    'ROI questions'
                ],
                'response_strategies': {
                    'cost': ['Value demonstration', 'ROI calculation', 'Flexible options'],
                    'timeline': ['Phased approach', 'Quick wins', 'Support plan'],
                    'technical': ['Proof of concept', 'Technical deep dive', 'Integration support']
                },
                'reinforcement_points': [
                    'Value demonstration',
                    'Success stories',
                    'Guarantee terms'
                ],
                'psychological_considerations': [
                    'Address emotional concerns',
                    'Build confidence',
                    'Reduce perceived risk'
                ]
            },
            'value_presentation': {
                'messaging_sequence': [
                    'Pain point acknowledgment',
                    'Solution overview',
                    'Benefits demonstration',
                    'Proof points',
                    'Next steps'
                ],
                'benefit_framework': {
                    'emotional': ['Peace of mind', 'Confidence', 'Success'],
                    'rational': ['Cost savings', 'Efficiency', 'Performance'],
                    'social': ['Market leadership', 'Innovation', 'Recognition']
                },
                'proof_points': [
                    'Case studies',
                    'Testimonials',
                    'Industry recognition'
                ]
            },
            'conversion': {
                'opportunity_signals': [
                    'Active engagement',
                    'Detailed questions',
                    'Timeline discussion',
                    'Budget discussion',
                    'Stakeholder involvement'
                ],
                'risk_mitigation': [
                    'Clear guarantees',
                    'Phased implementation',
                    'Regular reviews',
                    'Success metrics',
                    'Exit clauses'
                ],
                'readiness_signals': [
                    'Budget confirmation',
                    'Timeline agreement',
                    'Stakeholder buy-in',
                    'Technical validation',
                    'Contract review'
                ]
            },
            'psychological_guidance': {
                'emotional_triggers': [],
                'personality_insights': {
                    'traits': [],
                    'preferences': []
                },
                'persuasion_patterns': [],
                'rapport_building': [],
                'state_tracking': {
                    'emotional': {},
                    'cognitive': {},
                    'behavioral': {}
                }
            }
        } 