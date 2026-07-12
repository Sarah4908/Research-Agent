# AI Research Agent

An AI-powered research assistant built on **IBM watsonx Orchestrate**, developed for the AICTE/Edunet Foundation internship — Problem Statement 1: Research Agent.

The agent helps with academic and scientific research tasks: it searches arXiv for relevant literature, summarizes papers, organizes references, suggests research hypotheses, and drafts outline sections for research papers. It also supports direct PDF upload and analysis.

## Problem statement

> A Research Agent is an AI system designed to assist with academic and scientific research tasks. It can autonomously search for literature, summarize papers, and organize references. Using natural language processing, it understands research questions and retrieves relevant information. The agent can generate reports, suggest hypotheses, and even draft sections of research papers. It saves time by automating repetitive tasks like citation management and data extraction.
>
> **Technology:** Use of IBM Cloud Lite services / IBM Granite.

## Architecture

```
User
  │
  ▼
Streamlit frontend (chat UI + PDF upload)
  │
  ▼
watsonx Orchestrate agent (LLM on IBM Cloud)
  │
  ├──▶ Knowledge base (uploaded PDFs — RAG)
  │
  └──▶ arXiv search tool (live API retrieval via OpenAPI)
  │
  ▼
Structured response (Key Concepts, Summary, Suggested Hypotheses, Draft Outline, References)
```

The agent combines two retrieval methods:
- **RAG (Retrieval-Augmented Generation)** — a curated knowledge base of uploaded reference papers
- **Live tool-calling** — a custom arXiv Search tool (imported via OpenAPI spec) that queries `export.arxiv.org` directly, so the agent can find current literature beyond its training data

This hybrid approach was a deliberate design choice: RAG alone only knows about pre-loaded documents, while live search alone has no curated fallback. Combining both gives broader coverage with a reliable baseline.

## Features

- **Natural language research queries** — ask about any topic; the agent searches arXiv and synthesizes a structured report
- **PDF upload & analysis** — attach a paper directly in the chat; the agent extracts its text and analyzes findings, methodology, and contributions
- **Conversational memory** — follow-up questions retain context from prior turns and any attached paper
- **Structured output** — every response includes Key Concepts, Summary, Suggested Hypotheses, Draft Outline, and a References section with real, clickable arXiv links
- **Anti-hallucination guardrails** — the agent is explicitly instructed to only cite papers actually returned by its tools, and to say so honestly if no relevant results are found, rather than inventing citations
- **PDF/text export** — download any response for offline use

## Tech stack

| Layer | Technology |
|---|---|
| Agent orchestration | IBM watsonx Orchestrate |
| LLM | Foundation model hosted on IBM Cloud (via Orchestrate) |
| Literature retrieval | Custom arXiv Search tool (OpenAPI import) + uploaded-document knowledge base |
| Frontend | Streamlit (Python) |
| PDF parsing | pdfplumber |
| Auth | IBM Cloud IAM (API key → bearer token) |

## Project structure

```
.
├── app.py                    # Streamlit frontend
├── requirements.txt          # Python dependencies
├── arxiv_openapi_spec.yaml   # OpenAPI spec for the arXiv search tool (imported into Orchestrate)
├── .env.example              # Template for required environment variables
└── README.md
```

## Setup

### 1. IBM watsonx Orchestrate (agent side)

1. Create an agent in watsonx Orchestrate.
2. Under **Toolset → Add tool → OpenAPI**, import `arxiv_openapi_spec.yaml`.
3. Under **Knowledge**, upload reference PDFs to give the agent a curated knowledge base.
4. Under **Behavior → Instructions**, configure the agent to search arXiv before answering, structure its output into the five sections above, and avoid fabricating citations if no relevant results are found.
5. Deploy the agent.
6. From the agent's **Channels → Embed** section, note the `orchestrationID`, `hostURL` (from **Show credentials**), and `agentId`.

### 2. Frontend (this repo)

Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file (see `.env.example`) with:

```
IBM_API_KEY=<your IBM Cloud IAM API key>
WXO_HOST_URL=<your Orchestrate service instance URL, from "Show credentials">
WXO_AGENT_ID=<your agent's ID>
```

Get your `IBM_API_KEY` from **IBM Cloud console → Manage → Access (IAM) → API keys**.

Run the app:

```bash
python -m streamlit run app.py
```

## API reference used

```
POST {WXO_HOST_URL}/v1/orchestrate/{AGENT_ID}/chat/completions
Authorization: Bearer <token from IBM IAM>
Content-Type: application/json

{
  "messages": [{"role": "user", "content": "<question>"}],
  "stream": false
}
```

## Evaluation

The agent was tested using Orchestrate's built-in evaluation tool across multiple queries, measuring tool-call accuracy, retrieval confidence, and response relevance — with consistent success rates across test runs. Tool-calling behavior was iteratively tightened (query relevance sorting, single-call-per-query instructions, explicit anti-hallucination guardrails) based on evaluation results.

## Notes

- `.env` is excluded from version control. Never commit real API keys — only variable names are documented here.
- Built entirely on IBM Cloud Lite services (watsonx Orchestrate), satisfying the problem statement's technology requirement.