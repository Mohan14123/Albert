"""AI Service Entrypoint."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Albert AI Service",
    description="Decoupled AI generation service for Albert Assistant.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # Optional direct run (use uvicorn ai.main:app --port 8001 in production)
    uvicorn.run(app, host="0.0.0.0", port=8001)
