# Multi-Agent Market Brief Assistant

## 🔧 Description
A multi-agent assistant that fetches market data, analyzes earnings reports, calculates portfolio exposure, and synthesizes natural language briefings — all accessible via voice or text in a Streamlit app.

## 🧱 Architecture

- **API Agent**: Market data via Yahoo + AlphaVantage
- **Scraping Agent**: Earnings from Yahoo
- **Retriever Agent**: FAISS-based RAG
- **Analysis Agent**: Portfolio exposure analysis
- **Language Agent**: GPT-based summarizer
- **Voice Agent**: Whisper + TTS
- **Orchestrator**: Routes calls
- **UI**: Streamlit

## ▶️ Run Locally

```bash
pip install -r requirements.txt
uvicorn agents.api_agent:app --port 8001
uvicorn agents.retriever_agent:app --port 8002
uvicorn agents.analysis_agent:app --port 8003
uvicorn agents.language_agent:app --port 8004
uvicorn orchestrator.main:app --port 8005
streamlit run streamlit_app/app.py
```

## 🚀 Docker

```bash
docker build -t market-assistant .
docker run -p 8501:8501 market-assistant
```
