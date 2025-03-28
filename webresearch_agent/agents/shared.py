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

class NarrativeSection(BaseModel):
    """Base model for narrative sections"""
    content: str = Field(description="Main narrative content")
    key_points: List[str] = Field(description="Key points from the narrative", default_factory=list)
    emotional_context: Dict[str, str] = Field(description="Emotional context and significance", default_factory=dict)

class ResearchNarrative(BaseModel):
    """Structure for research narratives"""
    story: NarrativeSection = Field(description="The main narrative describing findings and significance")
    context: NarrativeSection = Field(description="Detailed context about motivations and factors")
    examples: List[Dict[str, str]] = Field(description="Real-world examples and scenarios", default_factory=list)
    guidance: NarrativeSection = Field(description="Guidance for AI sales agents")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "story": {
                    "content": "A rich narrative describing the key findings...",
                    "key_points": ["First key insight", "Second key insight"],
                    "emotional_context": {
                        "primary_emotion": "confidence",
                        "underlying_needs": "security and validation"
                    }
                },
                "context": {
                    "content": "Detailed explanation of why these findings matter...",
                    "key_points": ["Motivation 1", "Motivation 2"],
                    "emotional_context": {
                        "pain_points": "fear of missing out",
                        "aspirations": "desire for growth"
                    }
                },
                "examples": [
                    {
                        "scenario": "Customer facing challenge X...",
                        "resolution": "How the solution helped...",
                        "key_learning": "What this illustrates..."
                    }
                ],
                "guidance": {
                    "content": "How to use these insights in sales conversations...",
                    "key_points": ["Conversation tip 1", "Conversation tip 2"],
                    "emotional_context": {
                        "tone": "empathetic and understanding",
                        "approach": "consultative and supportive"
                    }
                }
            }]
        }
    }

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

def create_narrative_prompt(role_description: str, narrative_focus: str) -> ChatPromptTemplate:
    """Creates a prompt template for narrative generation"""
    return ChatPromptTemplate.from_messages([
        ("system", f"""You are an expert at creating rich, insightful narratives about {role_description}.
        Your task is to analyze information and create a compelling narrative that helps AI sales agents 
        understand and connect with customers effectively.
        
        Create your narrative with these components:
        1. The Story: A flowing narrative that explains {narrative_focus}
        2. The Context: Deep insights into why things matter and how they connect
        3. Real Examples: Specific scenarios that illustrate key points
        4. AI Guidance: Clear advice on using these insights in sales conversations
        
        Focus on:
        - Creating natural, flowing narratives
        - Including emotional and psychological context
        - Explaining relationships and motivations
        - Providing specific, practical examples
        - Making insights actionable for AI agents
        
        Your response should help an AI agent understand both WHAT you've found and WHY it matters."""),
        ("human", """Information to analyze:
        {input_text}
        
        Create a narrative that helps AI sales agents understand and use these insights effectively.""")
    ])

def format_narrative_as_markdown(narrative: ResearchNarrative, section_title: str) -> str:
    """Formats a research narrative as Markdown"""
    sections = []
    
    # Add section title
    sections.append(f"## {section_title}\n")
    
    # Add the story
    sections.append("### The Story")
    sections.append(narrative.story.content)
    if narrative.story.key_points:
        sections.append("\n#### Key Insights")
        for point in narrative.story.key_points:
            sections.append(f"- {point}")
    
    # Add the context
    sections.append("\n### Understanding Why")
    sections.append(narrative.context.content)
    if narrative.context.key_points:
        sections.append("\n#### Key Factors")
        for point in narrative.context.key_points:
            sections.append(f"- {point}")
    
    # Add examples
    sections.append("\n### Real-World Examples")
    for i, example in enumerate(narrative.examples, 1):
        sections.append(f"\n#### Scenario {i}")
        sections.append(f"**Situation**: {example['scenario']}")
        sections.append(f"**Resolution**: {example['resolution']}")
        sections.append(f"**Key Learning**: {example['key_learning']}")
    
    # Add guidance
    sections.append("\n### Guidance for AI Sales Agents")
    sections.append(narrative.guidance.content)
    if narrative.guidance.key_points:
        sections.append("\n#### Key Recommendations")
        for point in narrative.guidance.key_points:
            sections.append(f"- {point}")
    
    return "\n".join(sections)

def combine_narratives(narratives: List[ResearchNarrative], title: str) -> str:
    """Combines multiple research narratives into a coherent story"""
    sections = [f"# {title}\n"]
    
    # Extract and combine key themes
    all_key_points = []
    for narrative in narratives:
        all_key_points.extend(narrative.story.key_points)
    
    sections.append("## Key Themes")
    for point in all_key_points:
        sections.append(f"- {point}")
    
    # Add individual narratives
    for i, narrative in enumerate(narratives, 1):
        sections.append(f"\n## Part {i}: {narrative.story.content[:50]}...")
        sections.append(narrative.story.content)
        
        sections.append("\n### Context")
        sections.append(narrative.context.content)
        
        if narrative.examples:
            sections.append("\n### Supporting Examples")
            for example in narrative.examples:
                sections.append(f"\n- **Scenario**: {example['scenario']}")
                sections.append(f"  **Outcome**: {example['resolution']}")
    
    # Add combined guidance
    sections.append("\n## Integrated Guidance for AI Sales Agents")
    all_guidance = []
    for narrative in narratives:
        all_guidance.extend(narrative.guidance.key_points)
    
    for point in all_guidance:
        sections.append(f"- {point}")
    
    return "\n".join(sections) 