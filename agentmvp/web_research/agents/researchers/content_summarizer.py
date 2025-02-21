from typing import Dict, List, Optional, ClassVar
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
import asyncio

class ContentSummarizerAgent:
    """Agent that processes website content and produces text summaries"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.chunk_size = 4000
        
        # Create prompts
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content analyst who extracts key company information that will be used by specialized research agents.
            Your task is to analyze website content and create a clear summary of the company that our agents can use for their research.
            
            Guidelines:
            1. Focus on factual information about the company
            2. Extract clear statements about what they do and how they operate
            3. Identify their target customers and market segments
            4. Capture their product/service descriptions
            5. Note any explicit claims or statements they make
            
            Format the output as a clear text summary with these sections:
            
            COMPANY IDENTITY
            - What they do (core business/mission)
            - Industry and market space
            - Target customers/users
            - Geographic presence
            
            PRODUCTS & SERVICES
            - Main offerings
            - Key features/capabilities
            - Service descriptions
            - Technical specifications
            
            MARKET POSITION
            - Customer segments served
            - Stated differentiators
            - Partner/client relationships
            - Industry focus areas
            
            COMPANY CLAIMS
            - Stated benefits
            - Performance claims
            - Success metrics
            - Customer promises"""),
            ("human", "Please analyze the following website content and extract key company information:\n\n{content}")
        ])
        
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks of roughly equal size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word)
            if current_size + word_size > self.chunk_size:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
                
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks

    async def analyze_content(self, content: str) -> str:
        """Analyze website content and produce a text summary"""
        try:
            if len(content) < self.chunk_size:
                formatted_prompt = self.analysis_prompt.format_messages(content=content)
                response = await self.llm.ainvoke(formatted_prompt)
                return response.content

            chunks = self._chunk_text(content)
            summaries = []
            
            for chunk in chunks:
                try:
                    formatted_prompt = self.analysis_prompt.format_messages(content=chunk)
                    response = await self.llm.ainvoke(formatted_prompt)
                    if response.content and response.content != "Error generating summary":
                        summaries.append(response.content)
                    await asyncio.sleep(1)  # Rate limit handling
                except Exception as e:
                    if "rate_limit_exceeded" in str(e):
                        await asyncio.sleep(20)  # Wait longer on rate limit
                        continue
                    raise e

            combined = " ".join(summaries)
            
            if len(combined) > self.chunk_size:
                await asyncio.sleep(2)  # Rate limit handling
                formatted_prompt = self.analysis_prompt.format_messages(content=combined)
                response = await self.llm.ainvoke(formatted_prompt)
                return response.content
                
            return combined
            
        except Exception as e:
            print(f"Error analyzing content: {str(e)}")
            return "Error generating summary"
    
    async def research(self, content: str) -> Dict:
        """Process website content and return text summary"""
        try:
            # Analyze the content
            summary = await self.analyze_content(content)
            
            return {
                "summary": summary,  # Now returns text instead of JSON
                "raw_content": content
            }
            
        except Exception as e:
            print(f"Error in research: {str(e)}")
            return {
                "summary": "Error generating summary",
                "raw_content": content
            } 