from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import mistune


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
    

    # Format the response with mistune
    markdown_renderer = mistune.create_markdown()
    formatted_response = markdown_renderer(response)
    
    # Add numbering to bold headings, ensure content stays on the same line
    formatted_response = add_numbered_headings(formatted_response)
    
    return formatted_response


def add_numbered_headings(text):
    """
    This function processes the markdown text to:
    1. Add numbered bold headings (with <br></br> to separate points).
    2. Ensure each point with its heading starts on the same line.
    3. Starts a new line only when a new heading appears.
    """
    # Regex to match bold headings and add numbers (1, 2, 3, ...)
    count = 1
    def replace_bold(match):
        nonlocal count
        heading = match.group(1).rstrip(":")  # Remove any trailing colon from the original heading
        # Add a single colon after the numbered heading
        result = f"<strong>{count}. {heading}</strong>:"
        count += 1
        return result

    # Replace bold headings with numbered bold headings
    text = re.sub(r"<strong>(.*?)</strong>:", replace_bold, text)  # Match existing colon after headings

    # Add <br></br> after each list item and paragraph to ensure proper line breaks
    text = re.sub(r"(<li>.*?</li>)", r"\1<br></br>", text)  # Add <br></br> after each list item
    text = re.sub(r"(<p>.*?</p>)", r"\1<br></br>", text)  # Add <br></br> after each paragraph
    
    # Ensure that after every new heading, there is a line break before it
    text = re.sub(r"(<strong>\d+\. .+?</strong>)", r"\n\1", text)
    
    return text


