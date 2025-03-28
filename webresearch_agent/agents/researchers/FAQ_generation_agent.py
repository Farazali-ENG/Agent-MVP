from typing import List, Dict, Any
import json
import re
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from ..base import ResearchAgentBase

class FAQGenerationAgent(ResearchAgentBase):
    def __init__(self, llm: ChatOpenAI):
        super().__init__(llm)
        self.parser = JsonOutputParser()

    def get_name(self) -> str:
        return "business_FAQs"

    def get_max_tokens(self, input_text: str, base_limit: int = 500, scale_factor: float = 0.5):
        """Dynamically determine max_tokens based on input size."""
        input_length = len(input_text.split())  # Count words
        estimated_tokens = int(input_length * scale_factor)  # Scale token count
        return min(max(estimated_tokens, 100), base_limit)  # Ensure min & max range

    def _setup(self):
        self.faq_generation_prompt = """
        Context:
        You are an expert at understanding businesses and anticipating customer questions.
        Your task is to analyze the provided business information and generate **at least 7 important questions** that customers would likely have about this business. Focus on questions that:
        1. Address core business offerings and value proposition
        2. Cover pricing and payment information
        3. Address common customer concerns
        4. Clarify service/product delivery
        5. Explain unique selling points
        6. Provide additional context about the business
        7. Highlight customer support and policies
        Format your response strictly as a **valid JSON object** with a key `"faqs"` containing an array of at least 7 objects.
        Ensure that your response contains **only the JSON object and nothing else**.
        If you cannot generate at least 7 questions, create broader or more general questions to meet the requirement.
        """
    async def research(self, queries: List[str]) -> Dict[str, Any]:
        """
        Generate top 7+ most relevant FAQs about a business based on the provided business information.
        Args:
            queries (List[str]): List containing:
                - First element: Company name
                - Second element: Website content summary
        Returns:
            Dict[str, Any]: Dictionary containing the generated FAQs
        """
        if len(queries) < 2:
            raise ValueError("Need both company name and website content")
        human_prompt = f"""Based on the following business information, generate the top 5 most relevant questions
        that customers would likely have. Make the questions specific to this business and its offerings:
        Company Name: {queries[0]}
        Website Content:
        {queries[1]}
        """
        messages = [
            SystemMessage(content=self.faq_generation_prompt),
            HumanMessage(content=human_prompt)
        ]
        max_tokens = self.get_max_tokens(human_prompt)
        response = await self.llm.ainvoke(messages, max_tokens=max_tokens)
        if isinstance(response, AIMessage):
            response_text = response.content
        else:
            response_text = response
        # First attempt: Fix and parse JSON directly
        try:
            fixed_json = self._fix_json(response_text)
            result = json.loads(fixed_json)
            # Verify "faqs" key exists
            if "faqs" not in result or not isinstance(result["faqs"], list):
                raise ValueError("Missing or invalid 'faqs' key in JSON response")
            return {"faqs": result["faqs"]}
        except json.JSONDecodeError as e:
            # Second attempt: Try a more aggressive fix by extracting individual FAQs
            try:
                # Extract and fix each FAQ individually if possible
                faqs_pattern = r'"question"\s*:\s*"([^"]*)"\s*,\s*"answer"\s*:\s*"([^"]*)"'
                matches = re.findall(faqs_pattern, response_text)
                if matches:
                    faqs = [{"question": q, "answer": a} for q, a in matches]
                    return {"faqs": faqs}
                else:
                    raise ValueError(f"Could not extract FAQs from response: {str(e)}")
            except Exception as extraction_error:
                raise ValueError(f"Invalid JSON output even after fixing: {str(e)}")
        


    def _fix_json(self, text: str) -> str:
        """Extracts, sanitizes, and fixes malformed JSON from LLM response."""
        text = text.strip()
        # Step 1: Extract JSON block from text - look for code blocks first
        json_block_pattern = r"```(?:json)?\s*(.*?)\s*```"
        code_blocks = re.findall(json_block_pattern, text, re.DOTALL)
        if code_blocks:
            text = code_blocks[0]  # Use the first code block found
        else:
            # If no code blocks, find the outermost JSON object
            json_pattern = r"\{.*\}"
            matches = re.findall(json_pattern, text, re.DOTALL)
            if matches:
                text = matches[0]  # Take the first valid JSON block
        # Step 2: Fix common JSON formatting issues
        text = text.replace("\n", " ")  # Remove newlines
        text = text.replace("\t", " ")  # Remove tabs
        text = re.sub(r',\s*}', '}', text)  # Remove trailing commas before }
        text = re.sub(r',\s*\]', ']', text)  # Remove trailing commas before ]
        # Step 3: Fix issues with quotes in field names and values
        text = re.sub(r'([{,]\s*)(\w+)(\s*:)', r'\1"\2"\3', text)  # Add quotes to unquoted field names
        # Step 4: Fix unclosed quotes in string values
        text = re.sub(r':\s*"([^"]*?)(?=[},])', r': "\1"', text)
        # Step 5: Handle truncated JSON
        if text.endswith(","):
            text = text[:-1]  # Remove dangling commas at end
        # Step 6: Ensure JSON is properly closed
        open_braces = text.count("{")
        close_braces = text.count("}")
        if open_braces > close_braces:
            text += "}" * (open_braces - close_braces)  # Close missing braces
        open_brackets = text.count("[")
        close_brackets = text.count("]")
        if open_brackets > close_brackets:
            text += "]" * (open_brackets - close_brackets)  # Close missing brackets
        # Step 7: Ensure proper structure by checking if it starts with { and ends with }
        if not text.startswith("{"):
            text = "{" + text
        if not text.endswith("}"):
            text += "}"
        return text



