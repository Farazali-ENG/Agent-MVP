from pydantic import BaseModel
from typing import Literal, List, Dict, Any


from ..default_prompts import state_transition_prompt, state_transition_output_format


# Simple state types
StateType = Literal["initial_greetings", "ask_name", "ask_clarification_questions", "offer_solution", "ask_biggest_concerns", "ask_what_prevents_from_making_decision", "lead_closing", "end_phase", "intermediate_phase"]
class ConversationState(BaseModel):
    """Core conversation state"""
    phase: StateType = "initial_greetings"
    history: List[Dict[str, str]] = []
    context: Dict[str, Any] = {}

class StateTransition(BaseModel):
    """Simple state transition output"""
    reason: str
    next_state: StateType


def update_conversation_state(state: ConversationState, psych_results: Dict[str, Any], llm) -> ConversationState:
    """Update conversation state with new information"""
    
    system_prompt = f"{state_transition_prompt}\n\n{state_transition_output_format}"
    user_prompt = f"""
Current Phase: {state.phase}

Recent Messages:
{state.history}

Psychological Analysis:
{psych_results}
"""
    
    completion = llm.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "assistant", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=StateTransition,
        temperature=0.1
    )
    response = completion.choices[0].message.parsed

    state.phase = response.next_state
    
    print(f"Next state: {state.phase}\nReason: {response.reason}\n\n")

    return state