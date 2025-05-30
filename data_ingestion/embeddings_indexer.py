from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

def build_index(texts: list):
    embedder = OpenAIEmbeddings()
    index = FAISS.from_texts(texts, embedding=embedder)
    return index

def retrieve(index, query: str, k: int = 3):
    return index.similarity_search(query, k=k)