from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.upload import router as upload_router
from app.api.routes.query import router as query_router


app = FastAPI(
    title="AI Agent RAG Backend",
    version="1.0.0"
)

# ----------------------
# CORS
# ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # senere: frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Health check
# ----------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ----------------------
# ROUTERS
# ----------------------
app.include_router(
    upload_router,
    prefix="/upload",
    tags=["upload"]
)

app.include_router(
    query_router,
    prefix="/query",
    tags=["query"]
)