"""Run sales conversation with AI agent"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Dict, Any
import os
import readchar
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.schema.language_model import BaseLanguageModel
from langchain_openai import ChatOpenAI
from openai import OpenAI

from salesagent.sales_manager.agents.state_transition import ConversationState
from salesagent.sales_manager.message_handler import handle_message


def read_research_data(file_path: str) -> Dict[str, Any]:
    """Read research data from a JSON file"""
    with open(file_path, 'r') as file:
        return json.load(file)
    
    return research_data


def main():

    # Initialize LLM
    # llm = ChatOpenAI(temperature=0.1)
    
    openai_client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Initialize state
    state = ConversationState()
    print("Starting conversation (type 'exit' to end)...")

    # Initialize research data
    research_data = read_research_data("salesagent/cache/research/research_results_tritownconstruction.json")
    
    response, state = handle_message(openai_client, state, "", research_results=research_data["research_results"], sales_strategy=research_data["sales_strategy"])
    print(f"\nAI Agent: {response}")
    while True:
        # Get user input

        user_input = input("\nCustomer: ")
        
        if user_input.lower() == 'exit':
            print("\nEnding conversation. Goodbye!")
            break

        # Process message
        response, state = handle_message(openai_client, state, user_input, research_results=research_data["research_results"], sales_strategy=research_data["sales_strategy"])

        # Print response
        print(f"\nAI Agent: {response}")

if __name__ == "__main__":
    main() 