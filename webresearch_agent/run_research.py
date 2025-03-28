
import os
from langchain_openai import OpenAI
from dotenv import load_dotenv
import asyncio
from .manager import WebResearchManager
load_dotenv()

async def main():
    llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.1) # Replace with your actual LLM instance
    manager = WebResearchManager(llm)
    result = await manager.research_company("well", website="https://www.thewellbeingcompany.com/")
    print(result)

asyncio.run(main())