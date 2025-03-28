from typing import Dict, List, Optional, ClassVar
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
import asyncio
import tiktoken

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

    def _chunk_text_by_tokens(self, text: str, max_tokens: int = 3000) -> List[str]:
        """Split text into chunks based on token count."""
        # Ensure text is a string
        if text is None:
            return []
        
        if not isinstance(text, str):
            text = str(text)
        
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")  # Adjust model name accordingly
            tokens = encoding.encode(text)
            chunks = []
            for i in range(0, len(tokens), max_tokens):
                chunk_tokens = tokens[i:i + max_tokens]
                chunks.append(encoding.decode(chunk_tokens))
            return chunks
        except Exception as e:
            print(f"Error in chunking text: {str(e)}")
            # Fallback to character-based chunking
            return self._chunk_text(text)

    async def analyze_content(self, content: str, max_tokens: int = 3000) -> str:
        """Analyze website content and produce a text summary using recursive summarization."""
        try:
            # Validate input
            if content is None:
                return "No content provided to analyze"
            
            if not isinstance(content, str):
                content = str(content)
            
            if not content.strip():
                return "Empty content provided"
            
            # Process content in chunks
            chunks = self._chunk_text_by_tokens(content, max_tokens=max_tokens)
            if not chunks:
                return "Unable to process content"
            
            summaries = []

            for chunk in chunks:
                try:
                    formatted_prompt = self.analysis_prompt.format_messages(content=chunk)
                    response = await self.llm.ainvoke(formatted_prompt)
                    if response and hasattr(response, 'content') and response.content:
                        summaries.append(response.content)
                    await asyncio.sleep(1)  # Rate limit handling
                except Exception as chunk_error:
                    print(f"Error processing chunk: {str(chunk_error)}")
                    continue  # Skip problematic chunks instead of failing completely

            if not summaries:
                return "Unable to generate summary from content"
            
            combined_summary = " ".join(summaries)

            # Check if combined summary still exceeds token limit
            try:
                encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                if len(encoding.encode(combined_summary)) > max_tokens:
                    # Recursive summarization
                    return await self.analyze_content(combined_summary, max_tokens=max_tokens)
            except Exception as token_error:
                print(f"Error checking token count: {str(token_error)}")
                # Continue with the summary we have

            return combined_summary

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