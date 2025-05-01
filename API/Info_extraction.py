
from together import Together
import base64
import os
from openai import OpenAI
import openai
import openai
import csv

from dotenv import load_dotenv
import os
system_prompt = """
Act as a professional OCR model.
From the given image:
- Extract only the written text exactly as it appears without adding, interpreting, or correcting any information.
- After extracting the text, provide a very short summary based only on the visible content.
- If the image contains photos of individuals with their names written underneath, list their names clearly as team members.
Strictly do not add any extra information, assumptions, or commentary beyond what is present in the image.
"""

from dotenv import load_dotenv
import os
# Load variables from .env into the environment
load_dotenv()

# Access them using os.getenv
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


# # imageUrl = r"D:\IdeaSouq\team_image.png"
# imageUrls=r"D:\IdeaSouq\logo.png"
# for idx,model in enumerate(models):
#     print(f"the model {model} is being processed")
#     if idx<2:

#         output = image_to_text_openai(imageUrl, model)
#         with open('D:\IdeaSouq\logo_info.txt', 'a', encoding='utf-8') as f:
#             f.write(f"the generated output by Model: {model}\n")
#             f.write(output + "\n")
#             f.write("="*50 + "\n")  # separator between models
#     else:
#         output = image_to_text_open_source(imageUrl, model)
#         with open('D:\IdeaSouq\logo_info.txt', 'a', encoding='utf-8') as f:
#             f.write(f"the generated output by Model: {model}\n")
#             f.write(output + "\n")
#             f.write("="*50 + "\n")  # separator between models

# print("Completed")



# imageUrl = r"D:\IdeaSouq\team_image.png"
# import os
# Images = r"D:\IdeaSouq\Images"
# imageUrls = [
#     os.path.join(Images, img)
#     for img in os.listdir(Images)
#     if img.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"))
# ]
# Fahrengold_summary=r"D:\IdeaSouq\Summary_fahrengold"
# for idx,model in enumerate(models):
#     print(f"the model {model} is being processed")
#     for url in ImageUrls:
#         if idx<2:
#             output = image_to_text_openai(imageUrl, model)
#             with open(f'D:\IdeaSouq\{model}.txt', 'a', encoding='utf-8') as f:
#                 f.write(f"the generated output by Model: {model}\n")
#                 f.write(output + "\n")
#                 f.write("="*50 + "\n")  # separator between models
#         else:
#             output = image_to_text_open_source(imageUrl, model)
#             with open(f'D:\IdeaSouq\{model}.txt', 'a', encoding='utf-8') as f:
#                 f.write(f"the generated output by Model: {model}\n")
#                 f.write(output + "\n")
#                 f.write("="*50 + "\n")  # separator between models

# print("Completed")


# # meta-llama/Llama-3.2-11B-Vision




# import os

# # Folder containing images
# Images = r"D:\IdeaSouq\Images"
# # Folder to store summary text files (one per model)
# Fahrengold_summary = r"D:\IdeaSouq\Summary_fahrengold"

# # List of image file paths
# imageUrls = [
#     os.path.join(Images, img)
#     for img in os.listdir(Images)
#     if img.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff"))
# ]

# # Ensure the summary folder exists
# os.makedirs(Fahrengold_summary, exist_ok=True)

# # List of models
# models = [
#     "gpt-4.1-mini",
#     "gpt-4-vision",
#     "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
#     "Qwen/Qwen2.5-VL-72B-Instruct",
#     "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
#     "meta-llama/Llama-4-Scout-17B-16E-Instruct"
# ]

# # Iterate over models
# for idx, model in enumerate(models):
#     print(f"Processing model: {model}")
#     output_file_path = os.path.join(Fahrengold_summary, f"{model.replace('/', '_')}.txt")

#     # Iterate over each image
#     for image_path in imageUrls:
#         if idx < 2:
#             output = image_to_text_openai(image_path, model)
#         else:
#             output = image_to_text_open_source(image_path, model)

#         with open(output_file_path, 'a', encoding='utf-8') as f:
#             f.write(f"Image: {os.path.basename(image_path)}\n")
#             f.write(f"Model: {model}\n")
#             f.write(output + "\n")
#             f.write("=" * 80 + "\n")

# print("Completed")


# import json
# import pandas as pd
# def get_summary_fields(text_path,startup_name):
#     vision_model = os.path.splitext(os.path.basename(text_path))[0]
#     with open(text_path, "r", encoding="utf-8") as f:
#         context = f.read()
#     system_prompt = """
# You are an expert assistant trained to analyze startup pitch decks in a way that enables comparison across different versions of the same document. Your task is to:

# 1. Generate a detailed and structured summary of the pitch deck.
# 2. Extract specific business and investment-related fields into a clean, flat JSON format.

# ⚠️ Important Instructions:
# - Only use information explicitly provided in the text context. Do NOT include any external knowledge or inferred details.
# - All fields must be flat key-value string pairs. Do NOT use nested structures, arrays, or markdown.
# - If any field is not found in the input, return its value as "Not given".

# ✅ The output must be a valid JSON object with these **exact keys**:

# {
#   "summary": "...",
#   "Vision": "...",
#   "Industry Expertise": "...",
#   "Execution & Resourcefulness": "...",
#   "Emotional Intelligence": "...",
#   "Storytelling Skills": "...",
#   "Decision-Making": "...",
#   "Team": "...",
#   "Market": "...",
#   "Traction": "...",
#   "Strategic Fit (for Hub71)": "..."
# }

# 📝 Summary Formatting Guide:
# - The `"summary"` field must be a single string containing a detailed, well-written paragraph — **not a list**, **not bullet points**, and **not a nested object**.
# - This paragraph should integrate and narratively describe the following aspects **in flowing natural language**:
#     - Company mission and vision
#     - Products/services and their unique value
#     - Key milestones and traction
#     - Financials and revenue performance (if mentioned)
#     - Market size and opportunity
#     - Strategic partnerships or known clients
#     - Team and advisory composition
#     - Go-to-market plans or roadmap

# Your goal is to produce a comprehensive but concise business summary that can easily be compared across versions of the same pitch deck.
# """


#     try:
#         response = openai.chat.completions.create(
#             model="gpt-4-turbo",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Use This Context: {context}"}
#             ],
#             temperature=0
#         )
#         model_output = response.choices[0].message.content
#         print(f" the model output is {model_output}")
#         try:

#             parsed_output = json.loads(model_output)
#             print(f"Parsed output for startup {startup_name}:\n\n{parsed_output}")
            
#             # Convert JSON to DataFrame
#             df = pd.DataFrame([parsed_output])  # use a list of dict to treat each field as a column
            
#             # Save to CSV with startup_name
#             csv_file = f"GPT_4_Turbo{vision_model}{startup_name}.csv"
#             df.to_csv(csv_file, index=False)
#             print(f"Saved to {csv_file}")
#         except json.JSONDecodeError:
#             print("Error: Model output is not a valid JSON. Skipping this entry.")
#             return

#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
 
# Fahrengold_summary = r"D:\IdeaSouq\Summary_fahrengold"
# # List of image file paths
# all_text = [
#     os.path.join(Fahrengold_summary, txt)
#     for txt in os.listdir(Fahrengold_summary)
#     if txt.lower().endswith((".txt"))
# ]
# text_path=r"D:\IdeaSouq\Summary_fahrengold\meta-llama_Llama-3.2-11B-Vision-Instruct-Turbo.txt"
# startup_name="FahrenGoold_Series_A"
# # for text_path in all_text:
# get_summary_fields(text_path,startup_name)

import json
import pandas as pd
import openai
import os

def get_summary_fields(context_text):
    summary_prompt="""You are a meticulous business analyst trained to generate high-quality summaries of startup pitch decks using only the provided text context. Your goal is to produce a **single, well-structured paragraph** that captures the startup's story, value proposition, and business status — solely based on the given content.
⚠️ Strict Instructions:
- Do NOT use any external knowledge.
- Do NOT make assumptions, interpretations, or inferences.
- Only use the exact details explicitly found in the input.
- If something is not stated, do not mention or hint at it.

✅ The summary must:
- Be a single, flowing paragraph (no bullets, headings, or lists).
- Cover as many of these elements as possible — **but only if present** in the context:
    - Startup name and mission
    - Product/service description
    - Unique value or differentiation
    - Market size or target audience
    - Revenue model or business model
    - Traction, growth, or customer metrics
    - Financials or funding status
    - Founders or team
    - Partnerships or clients
    - Go-to-market plans
    - Strategic goals or vision

🎯 Goal:
Create a grounded, natural-language summary that accurately reflects only what’s in the provided input, useful for comparing across different versions of the same pitch deck.

Your output must contain **only** the summary paragraph — no markdown, no formatting, no headings, no commentary.
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
        summary = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": summary_prompt},
                {"role": "user", "content": f"Use this pitch deck context:\n\n{context_text}"}
            ],
            temperature=0
        )
        summary_res = summary.choices[0].message.content
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
        final_output=f"The Sumnmary of this pitch deck is :\n\n {summary_res} and the key fields are : \n\n {model_output}"\
       
        return final_output

        # try:
        #     parsed_output = json.loads(model_output)
        #     parsed_output['summary']=summary_res
        #     parsed_output["Startup name"] = startup_name  # ensure startup name is always filled
        #     return parsed_output
        #     # df = pd.DataFrame([parsed_output])
        #     # csv_file = f"GPT_4_Turbo_Summary_{startup_name.replace(' ', '_')}.csv"
        #     # df.to_csv(csv_file, index=False)
        #     # print(f"✅ CSV saved to: {csv_file}")
        # except json.JSONDecodeError:
        #     print("❌ Error: Model output is not a valid JSON. Skipping this entry.")
        #     return "❌ Error: Model output is not a valid JSON. Skipping this entry."

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return "error"
