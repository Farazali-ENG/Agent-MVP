"""Agent responsible for generating strategic conversation starters based on research."""

from typing import Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate

class ConversationStarterAgent:
    """Generates contextual conversation starters based on research insights"""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the agent with an LLM"""
        self.llm = llm
        self._setup()
        
    def _setup(self) -> None:
        """Setup the agent's prompts"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at crafting engaging conversation starters for sales conversations.
            
            Using the provided research insights about the company, product/service, and target customers,
            generate a variety of conversation starters that will effectively engage potential customers.
            
            If any research components are missing, focus on creating general conversation starters
            based on the information that is available. Never mention that data is missing - instead,
            craft the best possible starters with what you have.
            
            Focus on creating starters that:
            - Show understanding of likely pain points and challenges
            - Hint at relevant value propositions without being pushy
            - Feel contextual and personalized to the target audience
            - Invite natural engagement and response
            - Build initial trust and credibility
            
            Structure your response in these sections:
            
            # Initial Messages
            ## General Openers
            [3-4 general opening messages that work for most prospects]
            
            ## Pain Point Focused
            [2-3 messages that lead with understanding of specific challenges]
            
            ## Value Proposition Led
            [2-3 messages that subtly highlight key benefits]
            
            ## Trust Building
            [2-3 messages that establish credibility and expertise]
            
            # Follow-up Messages
            ## Check-in Messages
            [2-3 gentle follow-up messages for prospects who haven't responded]
            
            ## Engagement Hooks
            [2-3 messages offering valuable insights/information to spark interest]
            
            ## Re-engagement
            [2-3 messages for re-engaging prospects after longer periods]
            
            # Lead Conversion Messages
            ## Contact Request
            [2-3 natural ways to ask for contact information]
            
            ## Follow-up Value Props
            [2-3 messages explaining the value of sharing contact details]
            
            ## Next Steps
            [2-3 messages setting expectations for follow-up]"""),
            ("human", """Generate conversation starters based on this research:
            
            Research Data:
            {research}""")
        ])
        
    async def research(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Generate conversation starters based on research data
        
        Args:
            query: Dict containing research data with company info, value props, etc.
            
        Returns:
            Dict containing conversation starters as raw text
        """
        try:
            research_data = query.get("research_data", {})
            
            # Format inputs from research data
            messages = self.analysis_prompt.format_messages(
                research=research_data
            )
            
            # Generate starters
            response = await self.llm.ainvoke(messages)
            
            # Return raw response
            return {"conversation_starters": response.content}
            
        except Exception as e:
            print(f"Error generating conversation starters: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"conversation_starters": ""} 