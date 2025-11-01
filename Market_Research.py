import cycls
import os
import json
import requests
from typing import List, Dict
from ui import header, intro

Header = """
# Market Research Agent

Get instant competitive intelligence and market analysis for any company.

**What I do:**
- Research companies and their competitors
- Analyze market positioning and differentiators
- Generate comparison tables with key features and pricing
- Provide actionable insights from multiple sources
"""

agent = cycls.Agent(pip=["requests", "openai", "python-dotenv"], copy=[".env"])
EXA_BASE_URL = "https://api.exa.ai"

def exa_request(api_key: str, endpoint: str, payload: Dict) -> List[Dict]:
    """Make request to Exa API"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{EXA_BASE_URL}/{endpoint}", headers=headers, json=payload, timeout=30)
        return r.json().get("results", [])
    except Exception:
        return []

def perform_research(exa_key: str, openai_client, company_name: str) -> str:
    """Perform market research for a company"""
    searches = [
        (f"{company_name} official website about", 3),
        (f"competitors alternatives to {company_name}", 8),
        (f"{company_name} industry analysis comparison", 5)
    ]
    all_results = [r for q, n in searches for r in exa_request(exa_key, "search", {"query": q, "numResults": n, "useAutoprompt": True})]
    result_ids = list({r["id"]: r for r in all_results if "id" in r}.keys())[:15]
    contents = exa_request(exa_key, "contents", {"ids": result_ids, "text": True, "maxCharacters": 15000})
    sources = [{"url": c.get("url", ""), "title": c.get("title", ""), "text": c.get("text", "")[:2000]} for c in contents]
    
    prompt = f"""Based on sources about {company_name}:
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
    source_urls = list(set([s["url"] for s in sources if s["url"]]))[:10]
    return response + "\n\n---\n**Sources:**\n" + "\n".join([f"- {url}" for url in source_urls])

@agent(header=header, intro=intro)
async def market_research_agent(context):
    """Conversational market research agent"""
    import os
    from openai import OpenAI
    import dotenv
    
    dotenv.load_dotenv()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    messages = [{"role": "system", "content": """You are a helpful market research assistant. 
Your job is to chat with users and help them with market research.
- Greet users warmly and ask how you can help
- When they want market research, ask for the company name
- Once you have the company name, use the research_company tool to get detailed analysis
- Be conversational and helpful throughout"""}]
    
    messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in context.messages])
    
    tools = [{"type": "function", "function": {
        "name": "research_company",
        "description": "Performs detailed market research on a company and its competitors",
        "parameters": {"type": "object", "properties": {"company_name": {"type": "string", "description": "The company to research"}}, "required": ["company_name"]}
    }}]
    
    completion = openai_client.chat.completions.create(
        model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto", temperature=0.7
    )
    
    response_msg = completion.choices[0].message
    
    if response_msg.tool_calls:
        company_name = json.loads(response_msg.tool_calls[0].function.arguments)["company_name"]
        research_result = perform_research(os.getenv("EXA_API_KEY"), openai_client, company_name)
        return f"🔍 **Market Research for {company_name}**\n\n{research_result}"
    
    return response_msg.content

agent.cycls(prod=False)

