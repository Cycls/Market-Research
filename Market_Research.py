import cycls
import os
import json
import requests
from typing import List, Dict

# Initialize Cycls agent with required dependencies
agent = cycls.Agent(
    pip=["requests", "openai", "python-dotenv"],
    copy=[".env"] 
)

EXA_BASE_URL = "https://api.exa.ai"

def exa_search(api_key: str, query: str, num_results: int = 8) -> List[Dict]:
    """Search via Exa API"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"query": query, "numResults": num_results, "useAutoprompt": True}
    try:
        r = requests.post(f"{EXA_BASE_URL}/search", headers=headers, json=payload, timeout=30)
        return r.json().get("results", [])
    except Exception:
        return []

def exa_get_contents(api_key: str, ids: List[str]) -> List[Dict]:
    """Fetch content from Exa API"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"ids": ids, "text": True, "maxCharacters": 15000}
    try:
        r = requests.post(f"{EXA_BASE_URL}/contents", headers=headers, json=payload, timeout=30)
        return r.json().get("results", [])
    except Exception:
        return []

def perform_research(exa_key: str, openai_client, company_name: str) -> str:
    """Perform market research for a company"""
    company_results = exa_search(exa_key, f"{company_name} official website about", num_results=3)
    competitor_results = exa_search(exa_key, f"competitors alternatives to {company_name}", num_results=8)
    industry_results = exa_search(exa_key, f"{company_name} industry analysis comparison", num_results=5)
    
    all_results = company_results + competitor_results + industry_results
    result_ids = list({r["id"]: r for r in all_results if "id" in r}.keys())[:15]
    contents = exa_get_contents(exa_key, result_ids)
    sources = [{"url": c.get("url", ""), "title": c.get("title", ""), "text": c.get("text", "")[:2000]} for c in contents]
    
    prompt = f"""Based on the following sources about {company_name}:
{json.dumps(sources, indent=2)}

Provide:
1. Brief overview of {company_name}
2. 4-6 main competitors
3. Comparison table (markdown) with: Company, Category, Target Customer, Key Features, Pricing, Website
4. Key insights and differentiators"""
    
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.2
    )
    response = completion.choices[0].message.content
    source_urls = list(set([s["url"] for s in sources if s["url"]]))
    return response + "\n\n---\n**Sources:**\n" + "\n".join([f"- {url}" for url in source_urls[:10]])

@agent()
async def market_research_agent(context):
    """Conversational market research agent"""
    import os
    from openai import OpenAI
    import dotenv
    
    dotenv.load_dotenv()
    EXA_API_KEY = os.getenv("EXA_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not EXA_API_KEY or not OPENAI_API_KEY:
        return "⚠️ Please set EXA_API_KEY and OPENAI_API_KEY environment variables."
    
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    
    # Build conversation history
    messages = [{"role": "system", "content": """You are a helpful market research assistant. 
Your job is to chat with users and help them with market research.
- Greet users warmly and ask how you can help
- When they want market research, ask for the company name
- Once you have the company name, use the research_company tool to get detailed analysis
- Be conversational and helpful throughout"""}]
    
    for msg in context.messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Define tool for LLM to trigger research
    tools = [{
        "type": "function",
        "function": {
            "name": "research_company",
            "description": "Performs detailed market research on a company and its competitors",
            "parameters": {
                "type": "object",
                "properties": {"company_name": {"type": "string", "description": "The company to research"}},
                "required": ["company_name"]
            }
        }
    }]
    
    # Call LLM with tool option
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto", temperature=0.7
    )
    
    response_msg = completion.choices[0].message
    
    # Check if LLM wants to call the research tool
    if response_msg.tool_calls:
        tool_call = response_msg.tool_calls[0]
        company_name = json.loads(tool_call.function.arguments)["company_name"]
        research_result = perform_research(EXA_API_KEY, openai_client, company_name)
        return f"🔍 **Market Research for {company_name}**\n\n{research_result}"
    
    return response_msg.content

if __name__ == "__main__":
    agent.cycls(prod=False)