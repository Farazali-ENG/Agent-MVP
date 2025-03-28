from typing import Dict, List, Optional, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from pydantic import BaseModel, Field
from typing import List as TypeList
import json

class AgentState(BaseModel):
    """Pydantic model for agent state"""
    messages: Sequence[BaseMessage] = Field(description="Conversation history")
    next_steps: List[str] = Field(default_factory=list, description="Planned next steps")
    current_task: str = Field(description="Current task being executed")

class ToolRequest(BaseModel):
    """Pydantic model for tool requests"""
    tool: str = Field(description="Name of the tool to use")
    input: Dict = Field(description="Input parameters for the tool")

class ToolResponse(BaseModel):
    """Pydantic model for tool responses"""
    output: str = Field(description="Output from the tool")
    error: Optional[str] = Field(default=None, description="Error message if tool execution failed")

def create_specialized_agent(
    llm: BaseLanguageModel,
    tools: List[BaseTool],
    system_prompt: str
) -> RunnablePassthrough:
    """Create a specialized agent with the given tools and system prompt"""
    
    # Create a tools description for the system prompt
    tools_description = "\n\n".join([
        f"Tool: {tool.name}\nDescription: {tool.description}\n"
        for tool in tools
    ])
    
    # Create example using the pydantic model
    example = ToolRequest(
        tool="tool_name",
        input={"param": "value"}
    ).model_dump_json(indent=2)
    
    # Enhance system prompt with tools description
    system_message = f"""
    {system_prompt}
    
    You have access to the following tools:
    {tools_description}
    
    When you need to use a tool, format your response as a JSON object in this EXACT format (no other text):
    {example}
    
    Wait for the tool's response before proceeding.
    Your final response should also be a valid JSON object matching the expected schema.
    """
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{input}"),
    ])
    
    def parse_llm_response(response: str) -> Dict:
        """Parse LLM response and validate against pydantic models"""
        try:
            # Try parsing as tool request first
            return ToolRequest.model_validate_json(response).model_dump()
        except:
            # If not a tool request, return raw content
            return {"content": response}
    
    runnable = (
        RunnablePassthrough.assign(
            messages=lambda x: x.get("messages", [])
        )
        | prompt
        | llm
        | RunnableLambda(lambda x: parse_llm_response(x.content))
    )
    
    return runnable 