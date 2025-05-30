# from fastapi import FastAPI, Request
# import google.generativeai as genai
# import os
# from dotenv import load_dotenv

# load_dotenv()
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Configure the Gemini API
# genai.configure(api_key=GEMINI_API_KEY)

# # Create the FastAPI app
# app = FastAPI()

# # Use the correct model that supports generate_content
# model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# @app.post("/generate_summary")
# async def generate_summary(request: Request):
#     try:
#         data = await request.json()
#         context = data.get("context", "")
#         question = data.get("question", "")
#         prompt = f"{context}\n\nAnswer the following: {question}"

#         # Generate content from Gemini
#         response = model.generate_content(prompt)
#         return {"summary": response.text}

#     except Exception as e:
#         return {"error": str(e)}


from fastapi import FastAPI, Request
import google.generativeai as genai
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

app = FastAPI()

# Configure Gemini only if API key is available
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")
else:
    model = None
    logger.warning("Gemini API key not found")

@app.post("/generate_summary")
async def generate_summary(request: Request):
    try:
        data = await request.json()
        context = data.get("context", "")
        question = data.get("question", "")
        
        if not model:
            # Fallback response when Gemini is not available
            return {
                "summary": f"Based on the provided context: {context[:200]}... "
                          f"Regarding your question about {question}, please check current market data sources "
                          f"for real-time information about Asia tech stock exposure and earnings surprises."
            }
        
        prompt = f"""
        Context: {context}
        
        Question: {question}
        
        Please provide a concise financial analysis based on the context provided. 
        Focus on risk exposure and any earnings information mentioned.
        """

        response = model.generate_content(prompt)
        return {"summary": response.text}

    except Exception as e:
        logger.error(f"Error in generate_summary: {e}")
        return {
            "summary": f"Analysis unavailable due to technical error. "
                      f"Based on provided context, please review your Asia tech stock positions manually."
        }