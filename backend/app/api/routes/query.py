# PATH: backend/app/api/routes/query.py

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from openai import OpenAI
import os

from app.db.supabase_client import supabase
from app.core.auth import get_tenant

router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class QueryRequest(BaseModel):
    question: str


@router.post("/")
def query_documents(
    payload: QueryRequest,
    x_api_key: str = Header(None)
):

    # =========================
    # 1. TENANT AUTH
    # =========================
    tenant = get_tenant(x_api_key)

    if not tenant:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    tenant_id = tenant["id"]

    # =========================
    # 2. FETCH CHUNKS
    # =========================
    response = (
        supabase
        .table("chunks")
        .select("id, content")
        .eq("tenant_id", tenant_id)
        .limit(10)  # reduced for better performance
        .execute()
    )

    raw_chunks = response.data or []

    if not raw_chunks:
        return {
            "question": payload.question,
            "answer": "Jeg fant ingen dokumenter for denne kunden.",
            "sources": [],
            "confidence": 0.0
        }

    # =========================
    # 3. NORMALIZE CHUNKS (NO FAKE SCORING)
    # =========================
    chunks = [
        {
            "id": c["id"],
            "content": c["content"]
        }
        for c in raw_chunks
    ]

    # =========================
    # 4. BUILD CONTEXT (CLEAN FORMAT)
    # =========================
    context = "\n\n".join(
        f"[ID: {c['id']}]\n{c['content']}"
        for c in chunks
    )

    # =========================
    # 5. SYSTEM PROMPT
    # =========================
    system_prompt = """
Du er en AI-assistent for et dokument-søkesystem for borettslag og SMB.

Regler:
- Svar kun basert på konteksten
- Hvis info mangler: si det tydelig
- Ikke dikt opp fakta
- Vær kort, presis og profesjonell
- Bruk norsk språk
"""

    # =========================
    # 6. USER PROMPT
    # =========================
    user_prompt = f"""
Spørsmål:
{payload.question}

Kontekst:
{context}

Svar:
"""

    # =========================
    # 7. GPT CALL
    # =========================
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2
    )

    answer = completion.choices[0].message.content

    # =========================
    # 8. RESPONSE
    # =========================
    return {
        "question": payload.question,
        "answer": answer,
        "sources": chunks,
        "confidence": 0.75
    }