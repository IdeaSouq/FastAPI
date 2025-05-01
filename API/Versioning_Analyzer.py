
from together import Together
import base64
import os
import openai
import csv
from Info_extraction import get_summary_fields
import fitz  # PyMuPDF
from PIL import Image
import io
import tempfile
from dotenv import load_dotenv
import os
# Load variables from .env into the environment
load_dotenv()

# Access them using os.getenv
openai_key = os.getenv("OPENAI_API_KEY")
together_apikey=os.getenv("Together_AI")
os.environ["OPENAI_API_KEY"]=openai_key



# convert_pdf_to_images(pdf_path, output_folder, dpi=300):
# system_prompt = """
# Act as a professional OCR model.
# From the given image:
# - Extract only the written text exactly as it appears without adding, interpreting, or correcting any information.
# - After extracting the text, provide a very short summary based only on the visible content.
# - If the image contains photos of individuals with their names written underneath, list their names clearly as team members.
# Strictly do not add any extra information, assumptions, or commentary beyond what is present in the image.
# """
system_prompt = """
Act as a professional vision and OCR model.

Your task is to:
1. Describe exactly what you see in the image, including any visual content such as people, scenes, charts, logos, objects, or any notable elements. This must be strictly based on what is visually present — do not add or infer anything beyond the visible image.
2. Extract all the text from the image exactly as it appears — without correcting spelling, grammar, or formatting.
3. If the image contains individuals with names labeled below them (e.g., in team slides), extract and clearly list the names under a "Team Members:" section.
4. Provide a very short summary or interpretation of what the image conveys — but only based on direct visual and textual information.

⚠️ Strict Rules:
- Do NOT add, infer, guess, or assume any information not explicitly visible in the image.
- Do NOT include any external knowledge or context.
- Your output must be fully grounded in the image — what you *see* and what is *written*.
"""

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    image_url = f"data:image/png;base64,{base64_image}"
    return image_url

def image_to_text_open_source(image_path):
    client = Together(api_key=together_apikey)
    response = client.chat.completions.create(
        model="meta-llama/Llama-4-Scout-17B-16E-Instruct",
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

def extract_text_from_document(file_path):
    """
    Extract text from either a PDF (via OCR using Together API) or a plain text file.
    """
    extracted_text = []
    if file_path.lower().endswith((".txt", ".md")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return None

    try:
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return None

        pdf = fitz.open(file_path)
        if len(pdf) == 0:
            print("Error: PDF has no pages")
            pdf.close()
            return None

        for page_num in range(len(pdf)):
            try:
                page = pdf[page_num]
                matrix = fitz.Matrix(300 / 72, 300 / 72)
                pixmap = page.get_pixmap(matrix=matrix)

                image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_img:
                    image.save(temp_img.name)
                    image_path = temp_img.name

                text = image_to_text_open_source(image_path)
                extracted_text.append(text.strip())

                os.remove(image_path)

            except Exception as e:
                print(f"Error processing page {page_num+1}: {e}")

        pdf.close()
        return "\n\n".join(extracted_text)

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
def get_rich_comparision(file1, file2):
    print("Extracting context from file 1")
    context_file1 = extract_text_from_document(file1)

    print("Extracting context from file 2")
    context_file2 = extract_text_from_document(file2)

    print("Extracting info from file 1\n\n")
    extracted_info_1 = get_summary_fields(context_file1)

    print("Extracting info from file 2\n\n")
    extracted_info_2 = get_summary_fields(context_file2)
    system_prompt="""You are a professional pitch deck comparison analyst skilled in extracting meaningful, high-impact differences between two structured versions of a startup pitch deck.

Your job is to:
1. Compare the two sets of field-level data provided.
2. Identify only the most important semantic and strategic changes — such as shifts in tone, omissions, newly introduced information, business model updates, or financial adjustments.
3. Use neutral phrasing for missing or added content, e.g., “previously included” or “newly introduced.”

Your response must:
- Be written as a single, professional paragraph.
- Contain no more than 2 to 3 short, impactful sentences.
- Strictly reflect the input data — do not assume or infer anything.
- Be relevant to what matters to investors, such as positioning, financials, or strategic direction.
- If there are no meaningful changes, return exactly: **"No discrepancy found."**
"""
#     system_prompt = """
# You are a professional pitch deck comparison analyst skilled in extracting meaningful, high-impact differences between two structured versions of a startup pitch deck.

# Your task is to:
# 1. Compare the two sets of field-level data provided.
# 2. Identify only the most important semantic and syntactic changes — focus on business-critical shifts in messaging, omissions, tone, emphasis, or newly introduced information.
# 3. If a field appears in one version but is missing in the other, clearly state that using neutral phrasing like “previously included” or “newly introduced.”

# Your response must:
# - Be formatted as a concise **single paragraph** in a professional tone.
# - Contain no more than **2 to 3 short, impactful sentences**.
# - Avoid phrases like “version 1” or “version 2”.
# - Strictly reflect the content in the provided context — do **not infer or fabricate** anything.
# - If there are no meaningful changes between the two versions, return exactly: **"No discrepancy found."**

# ✅ Format your output in a style like this:

# **Updated information from latest pitch deck:**  
# The company has shifted focus to an AI-platform. Revenue growth has slowed to 10% p.a. (prev. 25%). Their target market has expanded to include enterprise clients.

# Only highlight critical changes that would matter to an investor or evaluator.
# """

    try:
        context = f"The Summary and extracted fields for previous pitch deck:\n\n{extracted_info_1}\n\nThe Summary and extracted fields for latest version:\n\n{extracted_info_2}"
        summary_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Use this pitch deck context:\n\n{context}"}
            ],
            temperature=0
        )

        final_output = summary_response.choices[0].message.content.strip()
        output_path=r"D:\IdeaSouq\comparision_summary.txt"
        with open(output_path, "a", encoding="utf-8") as f:

            f.write(f"\nComparison between these two files: {file1} and {file2}\n")
            f.write("=" * 60 + "\n")
            f.write(final_output.strip() + "\n")
            f.write("\n" + "-" * 60 + "\n")

        return final_output

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return "error"

# file1=r"D:\IdeaSouq\Summary_fahrengold\meta-llama_Llama-4-Scout-17B-16E-Instruct.txt"
# file2=r"D:\IdeaSouq\Summary_fahrengold\meta-llama_Llama-4-Scout-17B-16E-Instruct.txt"
# # file1=r"D:\IdeaSouq\version1.txt"
# # file2=r"D:\IdeaSouq\version2.txt"
# print(get_rich_comparision(file1,file2))