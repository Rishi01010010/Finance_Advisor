# from fastapi import FastAPI, Request
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# app = FastAPI()
# embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# index = None

# @app.post("/index")
# async def create_index(request: Request):
#     global index
#     data = await request.json()
#     texts = data.get("texts", [])
#     index = FAISS.from_texts(texts, embedding_model)
#     return {"status": "index_created", "count": len(texts)}

# @app.get("/retrieve")
# def retrieve(query: str, k: int = 3):
#     if index is None:
#         return {"error": "Index not built"}
#     results = index.similarity_search(query, k=k)
#     return {"results": [r.page_content for r in results]}


from fastapi import FastAPI, Request
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

try:
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
except Exception as e:
    logger.error(f"Error loading embedding model: {e}")
    embedding_model = None

index = None

@app.post("/index")
async def create_index(request: Request):
    global index
    try:
        data = await request.json()
        texts = data.get("texts", [])
        
        if not texts:
            return {"status": "no_texts", "count": 0}
            
        if not embedding_model:
            return {"status": "embedding_model_unavailable", "count": len(texts)}
            
        index = FAISS.from_texts(texts, embedding_model)
        logger.info(f"Index created with {len(texts)} texts")
        return {"status": "index_created", "count": len(texts)}
        
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        return {"status": "error", "error": str(e), "count": 0}

@app.get("/retrieve")
def retrieve(query: str, k: int = 3):
    try:
        if index is None:
            return {"results": [f"No index available. Using query as context: {query}"]}
            
        results = index.similarity_search(query, k=k)
        return {"results": [r.page_content for r in results]}
        
    except Exception as e:
        logger.error(f"Error in retrieve: {e}")
        return {"results": [f"Retrieval error. Query context: {query}"]}