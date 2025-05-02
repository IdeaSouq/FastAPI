
from together import Together
import base64
import os
from openai import OpenAI
import openai
import openai
import csv
import json
import pandas as pd
import openai
import os
from dotenv import load_dotenv
from web_scrap import scrape_urls
system_prompt = """
Act as a professional OCR model.
From the given image:
- Extract only the written text exactly as it appears without adding, interpreting, or correcting any information.
- After extracting the text, provide a very short summary based only on the visible content.
- If the image contains photos of individuals with their names written underneath, list their names clearly as team members.
Strictly do not add any extra information, assumptions, or commentary beyond what is present in the image.
"""

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")

os.environ["OPENAI_API_KEY"]=openai_key
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    image_url = f"data:image/png;base64,{base64_image}"
    return image_url

def image_to_text_open_source(image_path,model_name):
    client = Together(api_key="6241261e3ba0e424720421874778ee5a42e8247b1273ca754cbf06a513f7d3cd")
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": system_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": encode_image(image_path)
                        }
                    }
                ]
            }
        ]
    )

    return response.choices[0].message.content
def image_to_text_openai(image_path,model_name):
    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text":system_prompt},
                {
                    "type": "input_image",
                    "image_url": encode_image(image_path)}
            ],
        }],
    )

    return response.output_text
models=["gpt-4.1-mini","gpt-4-vision","meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo","Qwen/Qwen2.5-VL-72B-Instruct","meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo","meta-llama/Llama-4-Scout-17B-16E-Instruct"]





def get_summary_fields(context_text):
    summary_prompt = """
You are a precise business analyst trained to generate a high-quality, one-paragraph summary of a startup pitch deck using only the provided text. 
Do not use any external knowledge, assumptions, or inferences — rely solely on the input content. 
If the context contains hyperlinks, extract and list them. Your output must be in JSON format with two fields:

1. "summary": A single, well-structured paragraph that captures the startup’s story, value proposition, and business status — using only details present in the input.
2. "hyperlinks": A list of all URLs explicitly found in the context. If none, return an empty list.

The summary may include — only if stated:
- Startup name and mission
- Product or service
- Differentiation or unique value
- Market or audience
- Revenue or business model
- Traction or growth metrics
- Financials or funding
- Team or founders
- Clients or partnerships
- Go-to-market plans
- Strategic goals or vision

⚠️ Do not include bullet points or section headers. Only return a JSON object like:
{
  "summary": "Your paragraph here.",
  "hyperlinks": ["https://example.com"]
}
"""



    system_prompt = """You are a highly precise extraction assistant trained to analyze startup pitch decks and business documents. Your task is to:

🎯 Extract only the following specific business and investment-related fields from the provided context and return them as plain text.

⚠️ Strict Instructions:
- Use only the information explicitly present in the provided context.
- Do NOT include summaries, explanations, introductions, or inferred details.
- If a field is missing or not clearly mentioned, return its value as "Not given".
- Do NOT output JSON, markdown, bullet points, or lists.
- Output each field in the format: Field Name: Value
- Return one field per line, exactly matching the field names listed below.

✅ Required Fields (in this exact order):

Vision: ...
Industry Expertise: ...
Execution & Resourcefulness: ...
Emotional Intelligence: ...
Storytelling Skills: ...
Decision-Making: ...
Team: ...
Market: ...
Traction: ...
Strategic Fit (for Hub71): ...
Year of establishment: ...
Founders: ...
Industry/sector: ...
Revenue/financials: ...
Total market opportunity: ...
Funding raised so far: ...
Customer traction metrics: ...
Number of employees: ...
Location/headquarters: ...
Business model: ...
Product stage: ...
"""


    try:
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": summary_prompt},
                    {"role": "user", "content": f"Use this pitch deck context:\n\n{context_text}"}
                ],
                temperature=0
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            summary=parsed['summary']
            hyperlinks=parsed['hyperlinks']
            if hyperlinks:
                fields=scrape_urls(hyperlinks)
                summary+=f"\n\n The Extracted Info are : \n\n{fields}"
        except json.JSONDecodeError as e:
            print("JSON decoding failed:", e)
            print("Raw output was:", content)
            

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Use this pitch deck context:\n\n{context_text}"}
            ],
            temperature=0
        )
        model_output = response.choices[0].message.content
        print(f"\n🧠 Model Output:\n{model_output}\n")
        final_output=f"The Sumnmary of this pitch deck is :\n\n {summary} and the key fields are : \n\n {model_output}"\
       
        return final_output
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return "error"
