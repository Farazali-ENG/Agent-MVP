from typing import Dict, List, Any
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from ..base import ResearchAgentBase

class ProductServicesAgent(ResearchAgentBase):
    """Agent that analyzes company's products and services"""
    
    def __init__(self, llm: BaseLanguageModel):
        super().__init__(llm)

    def _setup(self):
        """Setup agent-specific components"""
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert product analyst who extracts detailed information about a company's products and services.
            
            Guidelines:
            1. Focus on identifying all products and services offered
            2. Extract key features and specifications
            3. Note pricing information if available
            4. Identify target markets for each product/service
            5. Capture unique selling points
            
            Format the output with these sections:
            
            # Core Offerings
            - Main products/services
            - Key features and capabilities
            - Target markets
            
            # Specifications
            - Technical details
            - Service levels
            - Implementation/delivery methods
            
            # Pricing & Packages
            - Price points (if available)
            - Package structures
            - Service tiers
            
            # Differentiators
            - Unique features
            - Competitive advantages
            - Special capabilities"""),
            ("human", """Company: {company_name}
            
            Website Summary:
            {website_content}
            
            Create a structured analysis of products and services to help AI sales agents understand the offerings.""")
        ])

    def get_name(self) -> str:
        return "product_services"

    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a specific section from the analysis content"""
        try:
            start = content.index(f"# {section_name}")
            next_section = content.find("\n# ", start + 1)
            if next_section == -1:
                return content[start:].strip()
            return content[start:next_section].strip()
        except ValueError:
            return ""

    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """Analyze products and services based on website summary
        
        Args:
            queries: List containing:
                - First element: Company name
                - Second element: Website content summary
                
        Returns:
            Dict containing structured product/service analysis
        """
        if len(queries) < 2:
            raise ValueError("Need both company name and website content")
            
        company_name = queries[0]
        website_content = queries[1]
        
        # Generate analysis
        messages = self.analysis_prompt.format_messages(
            company_name=company_name,
            website_content=website_content
        )
        response = await self.llm.ainvoke(messages)
        
        # Extract sections
        content = response.content
        return {
            "narrative": content,
            "components": {
                "core_offerings": self._extract_section(content, "Core Offerings"),
                "specifications": self._extract_section(content, "Specifications"),
                "pricing": self._extract_section(content, "Pricing & Packages"),
                "differentiators": self._extract_section(content, "Differentiators")
            }
        } 