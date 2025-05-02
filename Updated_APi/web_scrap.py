import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
load_dotenv()
from tavily import TavilyClient
import openai
import logging
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables
load_dotenv()

# Check for required API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")
if not TAVILY_API_KEY:
    logger.warning("TAVILY_API_KEY not found in environment variables. Web search functionality will not work.")
def search_by_sources(startup_name: str) -> Dict:

    """
    Search for startup information from specific sources like website, Crunchbase, and LinkedIn
    with fallback to general web search when specific handles aren't available.
    
    Args:
        startup_name: Name of the startup to research
        extraction_schema: JSON schema defining the structure for extraction
        
    Returns:
        Dict containing the extracted structured data from various sources
    """
    web_search_available = TAVILY_API_KEY is not None
    if web_search_available:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            search_tool = TavilySearchResults(api_key=TAVILY_API_KEY)
        except ImportError:
            logger.warning("langchain_community.tools.tavily_search not available. Install with 'pip install langchain-community'")
            web_search_available = False

    if not web_search_available:
        logger.warning("Web search functionality not available. Set TAVILY_API_KEY environment variable.")
        return {"error": "Web search functionality not available"}
    llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    # First search for the website, Crunchbase and LinkedIn handles
    handles_query = f"{startup_name} official website crunchbase linkedin profiles"
    handles_results = search_tool.invoke(handles_query)
    
    # Extract handles using LLM
    handles_prompt = f"""
Based on the search results below, identify the official website URL, Crunchbase profile URL, 
and LinkedIn company page URL for the startup: {startup_name}.

Search results:
{handles_results}

⚠️ Strict Instructions:
- Respond **only** with a valid JSON object.
- Do not include explanations, text, or markdown — just the JSON.
- Use the following structure:
{{
  "website_url": "...",
  "crunchbase_url": "...",
  "linkedin_url": "..."
}}
- If any value is missing, set it to null.
"""

    
    handles_messages = [
        SystemMessage(content="You are an expert at identifying company online profiles and URLs."),
        HumanMessage(content=handles_prompt)
    ]
    
    handles_response = llm.invoke(handles_messages)
    try:
        
        logger.info(f"Found handles for {startup_name}: {handles_response}")
        try:
            # Try to parse the response as JSON
            structured_data =json.loads(handles_response.content)
            return [url for _,url in structured_data.items()]
        except json.JSONDecodeError:
            return {"error": "Failed to extract structured data", "raw_response": handles_response.content}
            
    except Exception as e:
        logger.error(f"Error processing startup handles: {str(e)}")
        # Fallback to general search
        logger.info(f"Falling back to general search for {startup_name}")
        return "error"


def scrape_urls(urls):
    client = TavilyClient(TAVILY_API_KEY)
    system_prompt = """
You are a highly precise extraction assistant trained to analyze startup pitch decks and business documents. Your task is to extract structured data strictly from the provided context.

Instructions:
- Extract only the specified fields below, based strictly on the content in the provided context.
- Return results in a JSON format with all fields as keys.
- For any field not clearly present, assign the value "Not given".
- Include a short summary of the business or startup based only on the provided text.
- Detect and include the Website URL, Crunchbase URL, and LinkedIn URL if mentioned.
- Do NOT fabricate, assume, or infer any missing data.

Required output fields (keys):
{
  "Vision": "...",
  "Industry Expertise": "...",
  "Execution & Resourcefulness": "...",
  Emotional Intelligence: ...,
Storytelling Skills: ...,
  "Decision-Making": "...",
  "Team": "...",
  "Market": "...",
  "Traction": "...",
  "Year of establishment": "...",
  "Founders": "...",
  "Industry/sector": "...",
  "Revenue/financials": "...",
  "Total market opportunity": "...",
  "Funding raised so far": "...",
  "Customer traction metrics": "...",
  "Number of employees": "...",
  "Location/headquarters": "...",
  "Business model": "...",
  "Product stage": "...",
  "Website URL": "...",
  "Crunchbase URL": "...",
  "LinkedIn URL": "...",
  "Summary": "..."
}
"""
    response = client.extract(
        urls=urls,
        extract_depth="advanced"
    )
    res=response['results']
    urls=[]
    content=[]
    for d in res:
        urls.append(d['url'])
        content.append(f"  {d['raw_content']}")
    context="".join(content)
    try:
        context = f"Extract Info from thsi Context:\n\n{context}"
        summary_response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Use this pitch deck context:\n\n{context}"}
            ],
            temperature=0
        )

        
        try:
            final_output = summary_response.choices[0].message.content.strip()
            json_output = json.loads(final_output)
            return json_output
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
            print("Raw output was:\n", final_output)
            return {"error": "Invalid JSON", "raw_output": final_output}
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        return "error"

# startup_name="anthropic"
# name="Y COMBINATOR"
# NAME="auditoria"
# print(scrape_urls(search_by_sources(NAME)))