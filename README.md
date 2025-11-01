# Market Researcher

An AI agent for instant competitive intelligence and market analysis for any company.

**Live Demo:** https://market-researcher.cycls.ai/

---

## 🎯 About The Project

This AI agent provides instant market and competitive intelligence reports for any company. It researches competitors, analyzes market positioning, and generates comparison tables with key features and pricing to deliver actionable insights. The process begins by identifying a target company through conversation, then uses the **Exa.ai API** for deep searches. Finally, it sends the extracted content to the **OpenAI (GPT-4o mini)** model to analyze and structure the final report.

## 🛠️ Tech Stack

-   **Framework**: [Cycls](https://cycls.com/)
-   **Language**: Python
-   **APIs**:
    -   **OpenAI API (GPT-4o mini)**: For conversational logic and data analysis.
    -   **Exa.ai API**: For advanced, meaning-based search.

## 🚀 Getting Started

To run this project locally, clone the repository, create a `.env` file with your API keys (`CYCLS_API_KEY`, `OPENAI_API_KEY`, `EXA_API_KEY`), install dependencies, and run the agent.

```bash
# 1. Clone the repository
git clone [https://github.com/your-username/market-research-agent.git](https://github.com/your-username/market-research-agent.git)
cd market-research-agent

# 2. Create and populate your .env file
# Example: echo "OPENAI_API_KEY=sk-..." > .env
```
---

### Less is more
