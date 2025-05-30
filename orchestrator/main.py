# from fastapi import FastAPI, Request
# import requests

# app = FastAPI()

# @app.post("/brief")
# async def generate_brief(request: Request):
#     body = await request.json()
#     query = body.get("query", "")
#     portfolio = body.get("portfolio", {})
#     context = body.get("context", "")

#     # Retriever Agent
#     try:
#         index_res = requests.post("http://localhost:8002/index", json={"texts": [context]})
#         retrieve_res = requests.get("http://localhost:8002/retrieve", params={"query": query})
#         documents = retrieve_res.json().get("results", [])
#     except Exception as e:
#         documents = [f"[Retriever error] {str(e)}"]

#     # Analysis Agent
#     try:
#         exposure_res = requests.post("http://localhost:8003/risk_exposure", json={
#             "query": query,
#             "portfolio": portfolio
#         })
#         exposure = exposure_res.json().get("exposure", "")
#     except Exception as e:
#         exposure = f"[Exposure error] {str(e)}"

#     # Language Agent (Gemini)
#     try:
#         summary_res = requests.post("http://localhost:8004/generate_summary", json={
#             "context": "\n".join(documents),
#             "question": query
#         })
#         print("🔍 Summary Agent Status:", summary_res.status_code)
#         print("📩 Summary Agent Raw Response:", summary_res.text)

#         summary = summary_res.json().get("summary", "")
#     except Exception as e:
#         summary = f"[Summary error] {str(e)}"

#     return {
#         "documents": documents,
#         "exposure": exposure,
#         "summary": summary
#     }

from fastapi import FastAPI, Request
import requests
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.post("/brief")
async def generate_brief(request: Request):
    try:
        body = await request.json()
        query = body.get("query", "")
        portfolio = body.get("portfolio", {})
        context = body.get("context", "")
        texts = body.get("texts", [context] if context else [])
        
        logger.info(f"Received request - Query: {query}, Portfolio keys: {list(portfolio.keys())}")

        # Initialize response components
        documents = []
        exposure_data = {}
        summary = ""

        # Retriever Agent
        try:
            if texts:
                index_res = requests.post(
                    "http://localhost:8002/index", 
                    json={"texts": texts},
                    timeout=10
                )
                logger.info(f"Index response: {index_res.status_code}")
                
                retrieve_res = requests.get(
                    "http://localhost:8002/retrieve", 
                    params={"query": query, "k": 3},
                    timeout=10
                )
                if retrieve_res.status_code == 200:
                    documents = retrieve_res.json().get("results", [])
            else:
                documents = ["No context documents provided"]
                
        except Exception as e:
            logger.error(f"Retriever error: {e}")
            documents = [f"Retriever service unavailable: {str(e)}"]

        # Analysis Agent
        try:
            exposure_res = requests.post(
                "http://localhost:8003/risk_exposure", 
                json={"portfolio": portfolio},
                timeout=10
            )
            if exposure_res.status_code == 200:
                exposure_data = exposure_res.json()
            else:
                exposure_data = {"error": f"Analysis service returned {exposure_res.status_code}"}
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            exposure_data = {"error": f"Analysis service unavailable: {str(e)}"}

        # Language Agent (Gemini)
        try:
            summary_context = "\n".join(documents) if documents else "No context available"
            summary_res = requests.post(
                "http://localhost:8004/generate_summary", 
                json={
                    "context": summary_context,
                    "question": query
                },
                timeout=30
            )
            
            logger.info(f"Summary service status: {summary_res.status_code}")
            
            if summary_res.status_code == 200:
                summary_data = summary_res.json()
                summary = summary_data.get("summary", "No summary generated")
            else:
                summary = f"Summary service error: {summary_res.status_code}"
                
        except Exception as e:
            logger.error(f"Summary error: {e}")
            summary = f"Summary service unavailable: {str(e)}"

        response = {
            "documents": documents,
            "exposure": exposure_data,
            "summary": summary,
            "query": query,
            "status": "success"
        }
        
        logger.info("Response generated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Main orchestrator error: {e}")
        return {
            "error": f"Service error: {str(e)}",
            "status": "error"
        }