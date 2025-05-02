
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

system_prompt = """Act as a professional pitch deck visual analyst and you are very good at describing and extracting important aspects of the Pitch Deck.
Return all extracted information as a **single paragraph**. Do not separate content into sections or lists. Include everything — names, roles, brands, visual layouts — in a continuous, descriptive format that fully reflects the image. 
If the pitch deck includes any hyperlinks, extract and include those hyperlinks within the paragraph as well."""


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
def generate_question(context):
    categories = {
        "team": ["team", "founder", "leadership", "experience", "expertise", "skills"],
        "market": ["market", "competitive", "competition", "landscape", "segment", "size"],
        "product": ["product", "solution", "technology", "offering", "development", "mvp"],
        "business_model": ["business model", "revenue", "pricing", "monetization", "customer acquisition"],
        "traction": ["traction", "users", "customers", "growth", "metrics", "kpi"],
        "financial": ["financial", "funding", "investment", "cash flow", "runway", "capital"],
        "growth": ["growth", "expansion", "scaling", "strategy", "plan"],
        "regulatory": ["regulatory", "legal", "compliance", "license", "certification", "approval"]
    }

    system_prompt = f"""You are an assistant that generates a list of short, factual questions that could be asked directly to a startup based on a comparison of two pitch decks.

Do NOT mention 'pitch deck', 'each deck', or compare explicitly. Just write clear, standalone questions as if interviewing the startup, based only on the provided context.

Use the following categories to guide the types of questions you ask:
{categories}

✅ Focus on areas like product, business model, traction, financials, team, etc., if they are present in the context.
❌ Do NOT generate hypothetical, speculative, emotional, or predictive questions.

All questions must be:
- Clearly answerable from the provided input
- Short and factual
- One question per line

Examples:
- What is your annual recurring revenue?
- How large is your target market?
- What is your customer acquisition cost?
- How many active users do you currently have?
"""


    try:
        user_prompt = f"Use this context to generate a list of factual comparison questions:\n\n{context}"
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        final_output = response.choices[0].message.content.strip()
        questions = [q.strip("- ").strip() for q in final_output.split("\n") if q.strip()]

        # Save to CSV
        with open("generated_questions.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Generated Questions"])
            for question in questions:
                writer.writerow([question])

        print("✅ Questions saved to generated_questions.csv")
        return questions

    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return "error"
file1=r"D:\IdeaSouq\LUXGEN AI_ Three-Year Financial Report (2022-2024).pdf"
file2=r"D:\IdeaSouq\latest.pdf"

# # file1=r"D:\IdeaSouq\version1.txt"
# # file2=r"D:\IdeaSouq\version2.txt"
# file=r"D:\IdeaSouq\test.txt"
# # summary=get_rich_comparision(file1,file2)
# # questions=generate_question(summary)

# context_file1 = extract_text_from_document(file)


# print("Extracting info from file 1\n\n")
# output_path=r"D:\IdeaSouq\comparision_summary.txt"
# extracted_info_1 = get_summary_fields(context_file1)
# print(extracted_info_1)
# with open(output_path, "a", encoding="utf-8") as f:
   
#     f.write(extracted_info_1  + "\n")
#     f.write("\n" + "-" * 60 + "\n")

