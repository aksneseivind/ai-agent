import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# ----------------------------
# ENV (local only)
# ----------------------------
load_dotenv()

# ----------------------------
# Validate environment
# ----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Missing OPENAI_API_KEY environment variable")

# ----------------------------
# OpenAI client
# ----------------------------
client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------------
# App init
# ----------------------------
app = FastAPI(title="AI Agent API", version="1.0")

# ----------------------------
# CORS (frontend access)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        # Add your exact Vercel domain here:
        "https://ai-agent.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Models
# ----------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str | None = None
    error: str | None = None

# ----------------------------
# Health endpoint
# ----------------------------
@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "ai-agent",
    }

# ----------------------------
# Chat endpoint
# ----------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant inside a CV-aware AI system. "
                        "Be concise, accurate, and structured."
                    ),
                },
                {
                    "role": "user",
                    "content": req.message,
                },
            ],
            temperature=0.6,
        )

        return ChatResponse(
            reply=response.choices[0].message.content
        )

    except Exception as e:
        return ChatResponse(
            error=str(e)
        )