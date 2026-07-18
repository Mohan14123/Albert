from fastapi import FastAPI
from app.api.v1 import auth, users, chats, messages, integrations, health
from app.api.internal import ai
from app.api.webhooks import providers

app = FastAPI(
    title="Albert Backend API",
    version="1.0.0",
    description="Backend API for Albert Assistant",
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(chats.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/internal")
app.include_router(providers.router)

@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass
