from typing import Dict, Any, List
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from ..default_prompts import psychological_analysis_prompt, state_transition_prompt


class PsychologicalAnalysis(BaseModel):
    key_concerns_or_interests: str
    trust_signals: str
    recommended_product_or_service_to_sell: str
    customer_confidence_in_the_product_or_service: str
    how_to_carry_the_conversation_forward: str


def analyze_psychology(llm, products_and_services: Dict, recent_messages: List[Dict[str, str]],
                       current_message: str ) -> Dict[str, str]:
    
    
    system_prompt = f"{psychological_analysis_prompt}\n\nConversation Phases and Objectives:\n{state_transition_prompt}"
    user_prompt = f"""
Analyze this interaction:

Current Message:
{current_message}

Recent Messages:
{recent_messages}

Business Products and Services:
{products_and_services}
"""

    completion = llm.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "assistant", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        response_format=PsychologicalAnalysis
    )

    response = completion.choices[0].message.parsed

    return response.model_dump()

