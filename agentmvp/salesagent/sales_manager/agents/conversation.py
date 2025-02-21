from pydantic import BaseModel
from typing import Dict

from ..default_prompts import response_generation_prompt, initial_greeting_prompt, ask_name_prompt, ask_clarification_questions_prompt, offer_solution_prompt, ask_biggest_concerns_prompt, ask_what_prevents_from_making_decision_prompt, lead_closing_prompt, end_phase_prompt, intermediate_phase_prompt


class ResponseGeneration(BaseModel):
    """Response generation output"""
    chain_of_thought: str
    response: str

class GreetingMessage(BaseModel):
    """Greeting message output"""
    chain_of_thought: str
    greeting_message: str


def generate_response(llm, current_phase: str, psych_analysis: str,
                      conversation_context: Dict, customer_message: str, relevant_chunks: str) -> str:
    """Generate response using selected strategy"""

    if current_phase == "initial_greetings":
        state_prompt = initial_greeting_prompt
    elif current_phase == "ask_name":
        state_prompt = ask_name_prompt
    elif current_phase == "ask_clarification_questions":
        state_prompt = ask_clarification_questions_prompt
    elif current_phase == "offer_solution":
        state_prompt = offer_solution_prompt
    elif current_phase == "ask_biggest_concerns":
        state_prompt = ask_biggest_concerns_prompt
    elif current_phase == "ask_what_prevents_from_making_decision":
        state_prompt = ask_what_prevents_from_making_decision_prompt
    elif current_phase == "lead_closing":
        state_prompt = lead_closing_prompt
    elif current_phase == "end_phase":
        state_prompt = end_phase_prompt
    elif current_phase == "intermediate_phase":
        state_prompt = intermediate_phase_prompt
    

    system_prompt = f"{response_generation_prompt}\n\nCURRENT CONVERSATION PHASE AND OBJECTIVE:\n{state_prompt}"
    if relevant_chunks:
        system_prompt += f"\n\nRELEVANT INFORMATION FROM WEBSITE:\n{relevant_chunks}"
    user_prompt = f"""
Generate a concise chat response using these inputs:

Current Phase: {current_phase}

Psychological Analysis:
{psych_analysis}

Conversation Context:
{conversation_context}

Customer Message:
{customer_message}
"""
    
    completion = llm.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "assistant", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=ResponseGeneration,
        temperature=0.1
    )

    output = completion.choices[0].message.parsed

    return output.response


def generate_greeting(llm, greeting_messages: str) -> str:
    """Generate greeting response"""

    system_prompt = """
You are a sales manager. You are part of a chatbot for a business.
You will be provided with some sample greeting messages that can be used as a first message to a customer.
respond with one of the greeting messages as is.
"""
    user_prompt = f"""
Sample Greeting Messages:
{greeting_messages}
"""

    completion = llm.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "assistant", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=GreetingMessage,
        temperature=0.1
    )

    output = completion.choices[0].message.parsed

    return output.greeting_message
