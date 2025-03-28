from typing import Dict, List, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
import re
from ..base import ResearchAgentBase

class PainPointsAgent(ResearchAgentBase):
    """Agent specialized in identifying and analyzing customer pain points and objections."""
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)
        self.answer_generation_prompt = ChatPromptTemplate.from_messages([
 ("system", """You specialize in providing concise, persuasive responses to customer concerns and objections.
            - Keep responses brief (one or two sentences).
            - Provide clear, compelling answers.
            - No extra labels like 'Response:', just answer directly."""),
            ("human", """Website Content:
            {website_content}
            Concern/Objection: {item}
            Provide a short, persuasive response.""")
        ])
    def get_name(self) -> str:
        return "pain_points"
    
    def _setup(self) -> None:
        """Setup the agent with its prompts"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at understanding customer pain points, objection patterns, and solution gaps.
            
            Analyze the provided company information and create a structured analysis that helps AI sales agents understand:
            
            # Pain Points
            ## Core Challenges
            - Identify the biggest customer challenges.
            - Explain the emotional and business impact.
            - Rank severity and urgency.
            
            # Solution Gaps
            ## Competitive Weaknesses
            - What solutions have customers tried?
            - Why have they failed?
            - What gaps still exist?
            
            # Objections
            ## Common Objections
            - List frequent objections in sales conversations.
            - Explain the root concerns behind each.
            - Suggest counterarguments.
            
            # Customer Concerns   **Ensure this section is always generated**
            ## Key Concerns
            - What major fears or hesitations do customers have?
            - What proof points or reassurances are needed?
            - :small_blue_diamond: **Always provide at least three sssskey concerns.**
            
            # Sales Guidance
            ## Handling Strategies
            - What sales tactics can address these issues?
            - How can AI agents handle concerns effectively?
            """),
            ("human", """Company: {company_name}
Website Summary:
{website_content}
Generate a structured analysis of customer pain points, objections, and concerns.""")
        ])
    
    async def _generate_dynamic_answer(self, website_content: str, item: str) -> str:
        """Generate a dynamic answer for a concern or objection"""
        try:
            messages = self.answer_generation_prompt.format_messages(
                website_content=website_content,
                item=item
            )
            response = await self.llm.ainvoke(messages)
            content = response.content if isinstance(response, AIMessage) else str(response)
            return content.strip()
        except Exception as e:
            print(f"Error generating dynamic answer: {e}")
            return f"Our solution addresses the concern '{item}' with comprehensive support and tailored approaches."
    
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze customer pain points based on website summary."""
        if len(queries) < 2:
            raise ValueError("Need both company name and website content")
        company_name, website_content = queries
        # Generate analysis
        messages = self.analysis_prompt.format_messages(
            company_name=company_name,
            website_content=website_content
        )
        response = await self.llm.ainvoke(messages)
        content = response.content if isinstance(response, AIMessage) else response
        # Extract components
        result = {
            "narrative": content,
            "components": {
                "pain_points": self._extract_section(content, "Pain Points"),
                "solution_gaps": self._extract_section(content, "Solution Gaps"),
                "top_concerns": await self._process_concerns(content, website_content),
                "objections": await self._process_objections(content, website_content),
                "sales_guidance": self._extract_section(content, "Sales Guidance")
            }
        }
        return result
    async def _process_concerns(self, content: str, website_content: str) -> List[Dict[str, str]]:
        """Process concerns with dynamic answer generation"""
        concerns = self._parse_list_items(
            self._extract_section(content, "Customer Concerns"),
            "Key Concerns"
        )
        # Generate dynamic answers
        processed_concerns = []
        for concern in concerns:
            # If no answer or very short answer, generate a dynamic one
            if not concern.get('answer') or len(concern['answer']) < 50:
                concern['answer'] = await self._generate_dynamic_answer(
                    website_content,
                    concern.get('concern', 'Generic Customer Concern')
                )
            processed_concerns.append(concern)
        return processed_concerns
    async def _process_objections(self, content: str, website_content: str) -> List[Dict[str, str]]:
        """Process objections with dynamic answer generation"""
        objections = self._parse_list_items(
            self._extract_section(content, "Objections"),
            "Common Objections"
        )
        # Generate dynamic answers
        processed_objections = []
        for objection in objections:
            # If no answer or very short answer, generate a dynamic one
            if not objection.get('answer') or len(objection['answer']) < 50:
                objection['answer'] = await self._generate_dynamic_answer(
                    website_content,
                    objection.get('objection', 'Generic Sales Objection')
                )
            processed_objections.append(objection)
        return processed_objections
    # Keep other existing methods (_extract_section, _parse_list_items) from the original implementation
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extracts specific sections from the structured LLM response."""
        start = content.find(f"# {section_name}")
        if start == -1:
            print(f" Section '{section_name}' not found!")
            return ""
        next_section = content.find("\n# ", start + 1)
        extracted = content[start:] if next_section == -1 else content[start:next_section]
        return extracted.strip()
    def _parse_list_items(self, content: str, subheader: str) -> List[Dict[str, str]]:
        """Parse structured concerns or objections from text, supporting nested bullet points."""
        pattern = rf"## {subheader}?.*?\n([\s\S]+?)(?:\n## |\Z)"
        match = re.search(pattern, content)
        if not match:
            print(f"No match found for {subheader} in section:\n{content}")
            return []
        section_content = match.group(1).strip()
        items = []
        current_item = None
        current_response = ""
        for line in section_content.split("\n"):
            line = line.strip()
            if line.startswith("- "):
                if current_item:
                    items.append({"concern" if subheader == "Key Concerns" else "objection": current_item, "answer": current_response.strip()})
                current_item = line[2:].strip()
                current_response = ""
            elif line.startswith(" - "):
                current_response += line[6:].strip() + " "
        # Add the last item
        if current_item:
            items.append({"concern" if subheader == "Key Concerns" else "objection": current_item, "answer": current_response.strip()})
        return items