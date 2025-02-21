#!/usr/bin/env python3
import argparse
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv
from agentmvp.web_research.manager import WebResearchManager
import asyncio
import traceback
import json
from rich.console import Console
from rich.markdown import Markdown
from langchain_openai import ChatOpenAI


load_dotenv()

console = Console()

def check_environment(llm: str):
    """Check required environment variables and dependencies"""
    if llm == "anthropic":
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please add it to your .env file"
            )
    elif llm == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            raise EnvironmentError(
                "OPENAI_API_KEY not found in environment variables. "
                "Please add it to your .env file"
            )

async def async_run_research(company, website):
    try:
        # Check environment setup
        check_environment("openai")
        
        # Initialize LLM
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Run research
        console.print("\n[bold blue]Starting research...[/bold blue]")
        researcher = WebResearchManager(llm)
        results = await researcher.research_company(company, website)
        return results
    
    except Exception as e:
        print(f"Error in creating Sales Report. Error: {e}")
        return None

def run_research(company, website):
    return asyncio.run(async_run_research(company, website))