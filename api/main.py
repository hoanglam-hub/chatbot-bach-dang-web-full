from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import base64
from google import genai
from dotenv import load_dotenv

from ingestion.pipeline import load_and_chunk
from embedding.embedding import embed_and_store, load_vectorstore
from retrieval.retriever import get_retriever
from generation.generation import generation
from config.loader import vectorstore_path, llm_model

load_dotenv()

app = FastAPI()
gemini_api_key = os.getenv("GEMINI_API_KEY")
app.mount("/static", StaticFiles(directory="static"), name="static")

if not os.path.exists(vectorstore_path):
    chunks = load_and_chunk()
    vs = embed_and_store(chunks)
else:
    vs = load_vectorstore()
retriever = get_retriever(vs)

client = genai.Client(api_key=gemini_api_key)

prompt = (
    "You are an assistant for question-answering tasks. "
    "If you don't know the answer, say that you don't know. "
    "For greetings or casual conversation, respond naturally and friendly. "
    "Use only the provided context to answer. "
    "If the exact information is not explicitly stated in the context, "
    "you MUST say: 'I don't know. This information is not in the provided documents.' "
    "Do NOT infer, estimate, or use any external knowledge under any circumstances. "
    "Do not guess, use outside knowledge, or web information. "
    "Answer in the same language as the question. "
    "Keep your answer concise, maximum 7 sentences. "
    "Context: \n{context}\n\n"
    "Question: {question}"
)

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    image: Optional[str] = None

@app.get("/")
def read_root():
    return FileResponse("frontend/index.html")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question

    image_keywords = ["tạo ảnh", "tạo hình ảnh", "vẽ ảnh", "generate image", "draw", "create image"]
    wants_image = any(keyword in question.lower() for keyword in image_keywords)

    image_base64 = None

    if wants_image:
        answer = "Image generation feature is not activated yet."
    else:
        answer = generation(retriever, question, prompt)

    return ChatResponse(answer=answer, image=image_base64)

@app.post("/chat_with_image")
async def chat_with_image(
    question: str = Form(...),
    images: List[UploadFile] = File(...)
):
    images = images[:5]

    parts = []
    for image in images:
        image_bytes = await image.read()
        image_base64 = base64.b64encode(image_bytes).decode()
        parts.append({
            "inline_data": {
                "mime_type": image.content_type,
                "data": image_base64
            }
        })

    parts.append({
        "text": f"Answer in the same language as the question. Maximum 7 sentences.\n\nQuestion: {question}"
    })

    response = client.models.generate_content(
        model=llm_model,
        contents=[{"parts": parts}]
    )

    return {"answer": response.text}
