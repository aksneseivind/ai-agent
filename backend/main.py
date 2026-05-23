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
        "https://ai-agent-five-plum.vercel.app",
        "https://ai-agent-lvvc.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# MEMORY (MULTI DOCUMENT)
# ----------------------------
documents = {}

# ----------------------------
# HEALTH
# ----------------------------
@app.get("/")
def root():
    return {"status": "ok"}

# ----------------------------
# UPLOAD PDF
# ----------------------------
@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global documents

    try:
        pdf_bytes = await file.read()
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        documents[file.filename] = text

        return {
            "status": "document uploaded",
            "filename": file.filename,
            "chars": len(text),
            "documents": list(documents.keys())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# CHAT
# ----------------------------
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        # Build full context from ALL documents
        if not documents:
            context = "No documents uploaded."
        else:
            context = "\n\n".join(
                f"DOCUMENT: {name}\n{text}"
                for name, text in documents.items()
            )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Answer ONLY based on the document context. "
                        "If the answer is not found, say you cannot find it.\n\n"
                        f"DOCUMENTS:\n{context}"
                    )
                },
                {
                    "role": "user",
                    "content": req.question
                }
            ],
            temperature=0.3
        )

        return ChatResponse(
            answer=response.choices[0].message.content
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------------------
# DOCUMENT LIST
# ----------------------------
@app.get("/documents")
async def get_documents():
    return {
        "documents": list(documents.keys())
    }