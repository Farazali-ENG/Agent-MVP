from typing import Dict, Any
from langchain_core.language_models import BaseLanguageModel
import asyncio
import json
import os
from datetime import datetime
from rich.console import Console

from textwrap import shorten

from .tools.web_scraper import WebScraperTool
from .agents.researchers.FAQ_generation_agent import FAQGenerationAgent
from .agents.researchers.pain_points import PainPointsAgent
from .agents.strategy.builder import SalesStrategyBuilder

from langchain.text_splitter import RecursiveCharacterTextSplitter
console = Console()


class WebResearchManager:
    """Manages research operations across multiple specialized agents and stores results in JSON."""

    def __init__(self, llm: BaseLanguageModel):
        if hasattr(llm, 'temperature'):
            llm.temperature = 0.1  # Set LLM temperature for consistency

        self.llm = llm
        self.web_scraper = WebScraperTool()
        self.faq_agent = FAQGenerationAgent(llm)
        self.pain_points_agent = PainPointsAgent(llm)
        self.strategy_builder = SalesStrategyBuilder(llm)

    async def _execute_agent_research(self, agent, inputs):
        """Executes research using an agent and ensures valid JSON output."""
        try:
            result = await agent.research(inputs)

            # Convert result to dictionary if needed
            if isinstance(result, str):  
                try:
                    result = json.loads(result)  # Parse JSON string
                except json.JSONDecodeError as e:
                    console.print(f"[bold red]JSON Parsing Error: {str(e)}[/bold red]")
                    return {"faqs": []}  # Return empty FAQs instead of crashing

            # Ensure it's a dictionary
            return result if isinstance(result, dict) else {}

        except Exception as e:
            console.print(f"[bold red]Agent {agent.__class__.__name__} failed: {str(e)}[/bold red]")
            return {"faqs": []}



    def _save_results_to_json(self, company_name: str, results: dict):
        """Saves research results to a JSON file."""
        try:
            output_dir = "research_results"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/{company_name}_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=4, ensure_ascii=False)

            console.print(f"\n[bold green]Research results saved to {filename}[/bold green]\n")
        except Exception as e:
            console.print(f"[bold red]Failed to save results: {e}[/bold red]")


    async def research_company(self, company_name: str, website: str = None) -> dict:
        """Conducts research and extracts FAQs, top concerns, objections, and greeting messages."""
        try:
            initial_content = ""
            if website:
                console.print("\n[bold blue]Scraping website content...[/bold blue]")
                initial_content = await self.web_scraper._arun(website)
                console.print("\n[bold blue]Website content extracted.[/bold blue]")

            # Limit content to avoid exceeding token limits
            shortened_content = shorten(initial_content, width=4000, placeholder="...")

            console.print("\n[bold blue]Generating FAQs...[/bold blue]")
            faqs = await self._execute_agent_research(self.faq_agent, [company_name, shortened_content])

            console.print("\n[bold blue]Identifying top concerns...[/bold blue]")
            concerns = await self._execute_agent_research(self.pain_points_agent, [company_name, shortened_content])

            console.print("\n[bold blue]Generating greeting messages...[/bold blue]")
            greeting_messages = await self._generate_greeting_messages(company_name)

            # Correctly extract top_concerns and objections
            research_data = {
                "greeting_messages": greeting_messages,  # List of three greeting messages
                "FAQS": faqs.get("faqs", [])[:5],  
                "top_concerns": concerns.get("components", {}).get("top_concerns", [])[:2],  
                "objections": concerns.get("components", {}).get("objections", [])[:1]
            }

            self._save_results_to_json(company_name, research_data)
            return research_data

        except Exception as e:
            console.print(f"[bold red]Research failed: {str(e)}[/bold red]")
            raise
    async def _generate_greeting_messages(self, company_name: str) -> list:
        """Generates three different greeting messages using the LLM."""
        try:
            prompt = f"""
            Generate three friendly and engaging greeting messages for a sales chatbot representing {company_name}. 
            Make them concise, warm, and inviting.
            Provide them as a JSON list: ["message1", "message2", "message3"].
            """

            response = await self.llm.ainvoke(prompt)

            # Extract response content
            content = response.content if hasattr(response, "content") else str(response)

            # Try to parse JSON response
            try:
                greeting_messages = json.loads(content)
                if isinstance(greeting_messages, list) and len(greeting_messages) == 3:
                    return greeting_messages
            except json.JSONDecodeError:
                console.print("[bold red]Failed to parse greeting messages, using defaults.[/bold red]")

            # Fallback default messages
            
        except Exception as e:
            console.print(f"[bold red]Greeting message generation failed: {str(e)}[/bold red]")
            