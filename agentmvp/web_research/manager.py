from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseLanguageModel
import asyncio
import traceback
from datetime import datetime
import json
from pathlib import Path
from rich.console import Console

from .tools.web_scraper import WebScraperTool
from .agents.researchers.content_summarizer import ContentSummarizerAgent
from .agents.researchers.customer_psychology import CustomerPsychologyAgent
from .agents.researchers.pain_points import PainPointsAgent
from .agents.researchers.value_proposition import ValuePropositionAgent
from .agents.researchers.user_behavior import UserBehaviorAgent
from .agents.researchers.product_services import ProductServicesAgent
from .agents.base import ResearchAgentBase
from .agents.strategy.builder import SalesStrategyBuilder

console = Console()

class WebResearchManager:

    """Coordinates research across specialized agents"""
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        
        # Initialize core tools
        self.web_scraper = WebScraperTool()
        self.content_summarizer = ContentSummarizerAgent(llm)
        
        # Initialize research agents
        self.agents: Dict[str, ResearchAgentBase] = {
            agent.get_name(): agent
            for agent in [
                CustomerPsychologyAgent(llm),
                PainPointsAgent(llm),
                ValuePropositionAgent(llm),
                UserBehaviorAgent(llm),
                ProductServicesAgent(llm),
            ]
        }
        
        # Initialize strategy builder
        self.strategy_builder = SalesStrategyBuilder(llm)
    
    async def _summarize_content(self, content: str) -> str:
        """Get initial content summary to guide research"""
        try:
            summary_results = await self.content_summarizer.research([content])
            return summary_results.get("summary", "No summary available")
        except Exception as e:
            print(f"[ERROR] Content summarization failed: {str(e)}")
            return content
    
    async def _execute_agent_research(
        self, 
        agent_name: str, 
        agent: ResearchAgentBase, 
        company_name: str, 
        website_content: str
    ) -> tuple[str, Dict]:
        """Execute research with a single agent"""
        try:
            results = await agent.research([company_name, website_content])
            return agent_name, results
        except Exception as e:
            print(f"[ERROR] Agent {agent_name} failed: {str(e)}")
            return agent_name, {}  # Return empty dict instead of None
    
    async def research_company(
        self,
        company_name: str,
        website: str = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Coordinate research across all agents and build sales strategy"""
        try:
            # Get initial content if website provided
            initial_content = ""
            if website:
                console.print("\n[bold blue]Scraping website content...[/bold blue]")
                raw_content = await self.web_scraper._arun(website)
                
                console.print("\n[bold blue]Summarizing website content...[/bold blue]")
                initial_content = await self._summarize_content(raw_content)
                console.print("\n[bold blue]Website Summary:[/bold blue]")
                console.print(initial_content)
                console.print("=====================\n")
            
            # Execute research with all agents concurrently
            research_tasks = [
                self._execute_agent_research(agent_name, agent, company_name, initial_content)
                for agent_name, agent in self.agents.items()
            ]
            
            # Gather results while showing progress
            console.print("\n[bold blue]Executing research agents...[/bold blue]")
            research_results = {}
            for agent_name, narrative in await asyncio.gather(*research_tasks):
                if narrative:
                    research_results[agent_name] = narrative
            
            # Build sales strategy from research results
            console.print("\n[bold blue]Building Sales Strategy...[/bold blue]")
            strategy_results = await self.strategy_builder.build_strategy(research_results)
            
            # Combine results
            results = {
                "research": research_results,
                "strategy": strategy_results,
                "website_summary": initial_content,
                "products_services": research_results.get("product_services", {})
            }
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Research failed: {str(e)}")
            traceback.print_exc()
            raise 