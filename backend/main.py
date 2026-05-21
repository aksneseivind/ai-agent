import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

# ----------------------------
# CORS CONFIG (PRODUCTION SAFE)
# ----------------------------
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "https://*.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # IMPORTANT: must be False when using wildcard patterns
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.get("/")
def root():
    return {"status": "ok", "service": "ai-agent"}

# ----------------------------
# REQUEST MODEL
# ----------------------------
class ChatRequest(BaseModel):
    message: str

# ----------------------------
# CHAT ENDPOINT
# ----------------------------
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7
        )

        return {
            "reply": response.choices[0].message.content
        }

    except Exception as e:
        return {
            "error": str(e)
        }