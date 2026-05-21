import os
from fastapi import FastAPI, UploadFile, File
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
        "https://ai-agent-five-plum.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# GLOBAL MEMORY (CV TEXT)
# ----------------------------
cv_text = ""

# ----------------------------
# Health
# ----------------------------
@app.get("/")
def root():
    return {"status": "ok"}

# ----------------------------
# Upload PDF
# ----------------------------
@app.post("/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    global cv_text

    pdf_bytes = await file.read()
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    cv_text = text

    return {
        "status": "CV uploaded",
        "length": len(cv_text)
    }

# ----------------------------
# Chat
# ----------------------------
class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        context = cv_text if cv_text else "No CV uploaded."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an assistant that answers based on this CV:\n\n{context}"
                },
                {"role": "user", "content": req.message}
            ],
            temperature=0.7
        )

        return {
            "reply": response.choices[0].message.content
        }

    except Exception as e:
        return {"error": str(e)}