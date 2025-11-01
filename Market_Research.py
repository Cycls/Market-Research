import cycls, os, json, requests, asyncio, dotenv
from typing import List, Dict
from ui import header, intro
from openai import OpenAI

dotenv.load_dotenv()
agent = cycls.Agent(keys=[os.getenv("CYCLS_KEY_1"), os.getenv("CYCLS_KEY_2")], pip=["requests", "openai", "python-dotenv"], copy=[".env", "ui.py"])

def get_env(key: str) -> str:
    """Get env var with fallback to reading .env file"""
    val = os.getenv(key)
    if not val:
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.strip() and f'{key}=' in line:
                        val = line.split('=', 1)[1].strip().strip('"').strip("'")
                        os.environ[key] = val
                        break
        except: pass
    return val

def exa_request(api_key: str, endpoint: str, payload: Dict) -> List[Dict]:
    try: return requests.post(f"https://api.exa.ai/{endpoint}", headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload, timeout=30).json().get("results", [])
    except: return []

def perform_research(exa_key: str, openai_client, company_name: str) -> str:
    searches = [(f"{company_name} official website about", 3), (f"competitors alternatives to {company_name}", 8), (f"{company_name} industry analysis comparison", 5)]
    all_results = [r for q, n in searches for r in exa_request(exa_key, "search", {"query": q, "numResults": n, "useAutoprompt": True})]
    result_ids = list({r["id"]: r for r in all_results if "id" in r}.keys())[:15]
    contents = exa_request(exa_key, "contents", {"ids": result_ids, "text": True, "maxCharacters": 15000})
    sources = [{"url": c.get("url", ""), "title": c.get("title", ""), "text": c.get("text", "")[:2000]} for c in contents]
    prompt = f"Based on sources about {company_name}:\n{json.dumps(sources, indent=2)}\n\nProvide: 1. Brief overview of {company_name} 2. 4-6 main competitors 3. Comparison table (markdown) with: Company, Category, Target Customer, Key Features, Pricing, Website 4. Key insights and differentiators"
    response = openai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.2).choices[0].message.content
    source_urls = list(set([s["url"] for s in sources if s["url"]]))[:10]
    return response + "\n\n---\n**Sources:**\n" + "\n".join([f"- {url}" for url in source_urls])

@agent("market-researcher", header=header, intro=intro)
async def market_research_agent(context):
    dotenv.load_dotenv()
    api_key = get_env("OPENAI_API_KEY")
    if not api_key:
        yield "Error: OPENAI_API_KEY not found. Please set it in your .env file."
        return
    
    openai_client = OpenAI(api_key=api_key)
    messages = [{"role": "system", "content": "You are a helpful market research assistant. Your job is to chat with users and help them with market research. - Greet users warmly and ask how you can help - When they want market research, ask for the company name - Once you have the company name, use the research_company tool to get detailed analysis - Be conversational and helpful throughout"}]
    messages.extend([{"role": msg["role"], "content": msg["content"]} for msg in context.messages])
    tools = [{"type": "function", "function": {"name": "research_company", "description": "Performs detailed market research on a company and its competitors", "parameters": {"type": "object", "properties": {"company_name": {"type": "string", "description": "The company to research"}}, "required": ["company_name"]}}}]
    
    response_msg = openai_client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools, tool_choice="auto", temperature=0.7).choices[0].message
    
    if response_msg.tool_calls:
        company_name = json.loads(response_msg.tool_calls[0].function.arguments)["company_name"]
        loader = f'<div style="padding:24px;text-align:center;max-width:400px;margin:0 auto;"><div style="display:inline-flex;align-items:center;gap:12px;padding:16px;background:linear-gradient(135deg,#667eea15 0%,#764ba215 100%);border-radius:12px;border:1px solid #667eea40;"><div style="width:24px;height:24px;border:3px solid #e0e7ff;border-top-color:#667eea;border-radius:50%;animation:spin 0.8s linear infinite;"></div><div style="text-align:left;"><div style="font-weight:700;color:#3730a3;margin-bottom:4px;">🔍 Researching {company_name}</div><div style="font-size:13px;color:#64748b;">Gathering market data... This may take 30-60 seconds</div></div></div></div><style>@keyframes spin{{0%{{transform:rotate(0deg);}}100%{{transform:rotate(360deg);}}}}</style>'
        yield loader
        await asyncio.sleep(0.1)
        
        exa_key = get_env("EXA_API_KEY")
        if not exa_key:
            yield "Error: EXA_API_KEY not found. Please set it in your .env file."
            return
        
        research_result = perform_research(exa_key, openai_client, company_name)
        yield f"🔍 **Market Research for {company_name}**\n\n{research_result}"
    else:
        yield response_msg.content

agent.push(prod=True)
