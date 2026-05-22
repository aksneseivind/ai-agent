# PATH: backend/app/api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, Header, HTTPException
import uuid
import os

from app.db.supabase_client import supabase
from app.core.auth import get_tenant
from app.services.pdf_loader import extract_text_from_pdf

router = APIRouter()


@router.post("/")
async def upload_pdf(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):

    # =========================
    # 1. AUTH
    # =========================
    tenant = get_tenant(x_api_key)

    if not tenant:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    tenant_id = tenant["id"]

    # =========================
    # 2. VALIDATION
    # =========================
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )

    # =========================
    # 3. TEMP FILE
    # =========================
    temp_path = f"temp_{uuid.uuid4()}.pdf"

    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    try:

        # =========================
        # 4. EXTRACT TEXT
        # =========================
        full_text = extract_text_from_pdf(temp_path)

        if not full_text or not full_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF"
            )

        # =========================
        # 5. CHUNKING
        # =========================
        chunk_size = 800

        chunks = [
            full_text[i:i + chunk_size]
            for i in range(0, len(full_text), chunk_size)
        ]

        # =========================
        # 6. INSERT DOCUMENT
        # =========================
        document_payload = {
            "tenant_id": tenant_id,
            "filename": file.filename
        }

        doc_response = (
            supabase
            .table("documents")
            .insert(document_payload)
            .execute()
        )

        if not doc_response.data:
            raise HTTPException(
                status_code=500,
                detail="Failed to create document"
            )

        document_id = doc_response.data[0]["id"]

        # =========================
        # 7. INSERT CHUNKS
        # =========================
        chunk_rows = [
            {
                "document_id": document_id,
                "tenant_id": tenant_id,
                "content": chunk,
                "chunk_index": i
            }
            for i, chunk in enumerate(chunks)
        ]

        supabase.table("chunks").insert(chunk_rows).execute()

        # =========================
        # 8. RESPONSE
        # =========================
        return {
            "message": "PDF processed successfully",
            "document_id": document_id,
            "chunks_created": len(chunks)
        }

    finally:
        # =========================
        # 9. CLEANUP
        # =========================
        if os.path.exists(temp_path):
            os.remove(temp_path)