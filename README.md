# Market Research Agent

An AI agent for instant competitive intelligence and market analysis for any company.

**Live Demo:** [**Market Research Agent**](https://market-research-agent-280879789566.me-central1.run.app/)

---

## 🎯 About The Project

This agent is designed to be your intelligent assistant for market research. Instead of spending hours on manual research, you can simply ask the agent for information on any company, and it will do the hard work to provide you with a comprehensive and structured report.

### ✨ Key Features

-   Researches companies and their competitors.
-   Analyzes market positioning and differentiators.
-   Generates comparison tables with key features and pricing.
-   Provides actionable insights from multiple trusted sources.

## ⚙️ How It Works

The agent uses an advanced mechanism that combines intelligent search with the power of Large Language Models (LLMs) to deliver accurate results:

1.  **Understanding the Request**: The agent starts a conversation with the user to identify the target company.
2.  **AI-Augmented Search**: It uses the **Exa.ai API** to perform deep, targeted searches about the company, its competitors, and industry analysis.
3.  **Data Extraction**: It gathers the most relevant content from the top search results.
4.  **Analysis & Generation**: The collected data is sent to the **OpenAI (GPT-4o mini)** model with a precise prompt to summarize, analyze, and organize it into a comprehensive report.
5.  **Report Presentation**: It presents the user with a structured report containing an overview, a list of competitors, a comparison table, and key insights, citing the sources used.

## 🛠️ Tech Stack

-   **Framework**: [Cycls](https://cycls.com/)
-   **Language**: Python
-   **APIs**:
    -   **OpenAI API (GPT-4o mini)**: For conversational logic and data analysis.
    -   **Exa.ai API**: For advanced, meaning-based search.

## 🚀 Getting Started

To set up and run this project locally, follow these steps:

**1. Clone the Repository:**

```bash
git clone [https://github.com/your-username/market-research-agent.git](https://github.com/your-username/market-research-agent.git)
cd market-research-agent
```

**2. Install Dependencies:**

```bash
pip install -r requirements.txt
```

*(Ensure your `requirements.txt` file contains `cycls`, `openai`, `python-dotenv`, and `requests`)*

**3. Set Up Environment Variables:**

Create a new file named `.env` in the project's root directory and add your API keys as follows:

```
# .env file
CYCLS_API_KEY="sk-..."
OPENAI_API_KEY="sk-..."
EXA_API_KEY="..."
```

**4. Run the Agent:**

Use the `cycls` command-line interface to run the agent locally.

```bash
cycls run Market_Research.py
```

The agent should now be running and ready for interaction through the interface provided by `cycls`.

---

### Less is more
