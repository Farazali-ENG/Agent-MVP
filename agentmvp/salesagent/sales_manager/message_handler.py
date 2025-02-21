from typing import Dict, Any, List, Tuple

from ...salesagent.sales_manager.agents.psychology import analyze_psychology
from ...salesagent.sales_manager.agents.state_transition import update_conversation_state, ConversationState
from ...salesagent.sales_manager.agents.conversation import generate_response, generate_greeting
from ...retrieval_agent.chromadb_agent import retrieve_relevant


def handle_message(llm, state: ConversationState, message: str, chroma_collection, research_results: str = "",
                    sales_strategy: str = "") -> Tuple[str, ConversationState]:
    """Main function to handle incoming messages and generate responses"""

    greeting_messages = sales_strategy["components"]["conversation_starters"]

    # Handle initial greeting
    if message == "" and state.history == []:
        print("============================= Generating greeting ================================")

        response = generate_greeting(llm, greeting_messages)
        state.history.append({"role": "assistant", "content": response})
        state.history.append({"conversation_phase": "initial_greeting"})

        return response, state

    # Store customer message
    state.history.append({"role": "customer", "content": message})

    # Retrieve relevant information
    print("============================= Retrieving relevant information ================================")
    try:
        relevant_chunks = retrieve_relevant(chroma_collection, message)
        relevant_chunks = "\n".join(relevant_chunks)
        # print(f"Relevant chunks:\n{relevant_chunks}\n")
    except Exception as e:
        print(f"Error retrieving relevant information: {e}")
        relevant_chunks = ""

    # Analyze psychology
    print("============================= Analyzing psychology ================================")
    products_and_services = research_results["product_services"]
    psych_results = analyze_psychology(
        llm,
        {"products_and_services": products_and_services},
        state.history,
        message
    )

    print(f"Psychological analysis:\n{psych_results}\n")
    state.context["last_analysis"] = psych_results

    # Update state
    print("============================= Updating state ================================")
    state = update_conversation_state(
        state,
        psych_results,
        llm
    )

    # Generate response
    print("============================= Generating response ================================")
    response = generate_response(
        llm,
        state.phase,
        psych_results,
        state.context,
        relevant_chunks,
        message
    )

    state.history.append({"role": "agent", "content": response})
    state.history.append({"conversation_phase": state.phase})

    return response, state