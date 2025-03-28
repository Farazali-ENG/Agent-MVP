"""Agent responsible for generating strategic conversation starters based on research."""

from typing import Dict, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

class ConversationStarterAgent:
    """Generates contextual conversation starters based on research insights"""
    
    def __init__(self, llm: BaseLanguageModel):
        """Initialize the agent with an LLM"""
        self.llm = llm
        self.parser = JsonOutputParser()
        self._setup()
        
    def _setup(self) -> None:
        """Setup the agent's prompts"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at crafting engaging conversation starters for sales conversations. You are representing a company that is trying to sell a product/service to a potential customer.
            Using the provided research insights about the company, product/service, and target customers, generate a variety of conversation starters that will effectively engage potential customers.
            If any research components are missing, focus on creating general conversation starters based on the information that is available. Never mention that data is missing - instead, craft the best possible starters with what you have.
            The starters that you will generate are going to be used as greeting messages to potential customers by a chatbot.
             
            Focus on creating starters that:
            - Show understanding of likely pain points and challenges
            - Hint at relevant value propositions without being pushy
            - Feel contextual and personalized to the target audience
            - Invite natural engagement and response
            - Build initial trust and credibility
            
            Response Format:
            - Return a list of conversation starters that contains 5 conversation openers.
            - Your output should be a JSON array of strings, each string being a conversation starter.
            - There should be a key called "conversation_starters" in the JSON object and all the conversation starters should be in the array as its value.
            """),
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
            response = self.parser.parse(response.content)
            
            # Return raw response
            return response
            
        except Exception as e:
            print(f"Error generating conversation starters: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"conversation_starters": ""} 