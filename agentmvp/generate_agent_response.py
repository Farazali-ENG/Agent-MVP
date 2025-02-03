from openai import OpenAI
from dotenv import load_dotenv
import os
import markdown2
import re


load_dotenv()


def generate_response(business_info_json, agent_conf, product_data, user_message):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Format product data for prompt
    formatted_products = "\n".join([
        f"- {product['name']} - Price: {product['price'] if product['price'] else 'Not specified'}" 
        for product in product_data
    ])
    
    sys_prompt = f"""
**PERSONA**
You are an AI sales agent bot for a company with the name "{business_info_json["business_info"]["name"]}".

**SYSTEM PROMPT**    
{agent_conf["system_prompt"]}

**BUSINESS PRODUCTS**:
{formatted_products}

**ADDITIONAL KNOWLEDGE**:
{business_info_json["business_info"]["details"]}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "developer", "content": sys_prompt},
            {"role": "user", "content": user_message},
        ]
    )
    
    response = completion.choices[0].message.content
    
    html_content = markdown2.markdown(response)
    html_content = html_content.replace('\n', '').replace('\n\n', '')

    return html_content