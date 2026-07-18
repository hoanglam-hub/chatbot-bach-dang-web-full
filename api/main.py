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
    "Answer in the same language as the question. "
    "Keep your answer concise, maximum 7 sentences. "
    "When answering in English, use these English equivalents for Vietnamese historical terms: "
    "Nam Han = Southern Han dynasty, Ngo Quyen = King Ngo Quyen, "
    "Hoang Thao = General Hoang Thao, Nguyen Tat To = Commander Nguyen Tat To, "
    "Tran Hung Dao = General Tran Hung Dao, Bach Dang River = Bach Dang River. "
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
    print(f"DEBUG: question = {question}")

    image_keywords = ["tạo ảnh", "tạo hình ảnh", "vẽ ảnh", "generate image", "draw", "create image"]
    wants_image = any(keyword in question.lower() for keyword in image_keywords)
    print(f"DEBUG: wants_image = {wants_image}")

    image_base64 = None

    if wants_image:
        try:
            image_response = client.models.generate_content(
                model="gemini-3.1-flash-lite-image",
                contents=f"Generate a historical Vietnamese battle scene image: {question}",
            )
            print(f"DEBUG: parts = {image_response.candidates[0].content.parts}")
            for part in image_response.candidates[0].content.parts:
                print(f"DEBUG: part type = {type(part)}, has inline_data = {hasattr(part, 'inline_data')}")
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_base64 = base64.b64encode(part.inline_data.data).decode()
                    print(f"DEBUG: image found, base64 length = {len(image_base64)}")
                    break
            answer = "Here is the generated image based on your request."
        except Exception as e:
            print(f"Image generation error: {e}")
            answer = f"Image generation failed: {str(e)}"
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

    image_prompt = f"""You are a helpful assistant analyzing images from a water level monitoring system.

    The system uses color detection to identify water levels with these labels shown in the top-left corner:
    - "NONE": No water level detected, water is above all color markers
    - "CAO" (High): Water level is high, only the top red marker is visible
    - "TB" (Medium): Water level is medium, red and blue markers are visible  
    - "THAP" (Low): Water level is low, all three markers (red, blue, green) are visible

    The timestamp shown in yellow (format MM:SS or HH:MM:SS) indicates elapsed time.
    The colored rectangles with "+" signs are the color detection zones.

    Carefully observe all text, numbers, labels and colored boxes in the image.
    Answer in the same language as the question.
    Maximum 7 sentences.

    Question: {question}"""

    parts.append({
        "text": image_prompt
    })

    response = client.models.generate_content(
        model=llm_model,
        contents=[{"parts": parts}]
    )

    return {"answer": response.text}

