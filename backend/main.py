import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
import io

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://ai-agent-lvvc.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# MEMORY
# ----------------------------
document_text = ""

# ----------------------------
# HEALTH
# ----------------------------
@app.get("/")
def root():
    return {"status": "ok"}

# ----------------------------
# UPLOAD DOCUMENT
# ----------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global document_text

    try:
        pdf_bytes = await file.read()
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        document_text = text

        return {
            "status": "document uploaded",
            "chars": len(document_text)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# CHAT (FIXED CONTRACT)
# ----------------------------

class ChatRequest(BaseModel):
    message: str   # ✅ FIX: was question

class ChatResponse(BaseModel):
    message: str
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        context = document_text if document_text else "No document uploaded."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that can answer questions about uploaded documents. "
                        "Use the document as primary context when available. "
                        "If the answer is not in the document, say so clearly.\n\n"
                        f"DOCUMENT:\n{context}"
                    )
                },
                {
                    "role": "user",
                    "content": req.message   # ✅ FIX
                }
            ],
            temperature=0.3
        )

        return ChatResponse(
            message=req.message,
            answer=response.choices[0].message.content
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))