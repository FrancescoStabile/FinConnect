"""
FinConnect API - Entry Point

Applicazione FastAPI per Home Banking e Simulazione Investimenti.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, accounts, transfers, investments
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="FinConnect API",
    description="API per il prototipo di Home Banking FinConnect - Project Work",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(accounts.router, prefix=API_PREFIX)
app.include_router(transfers.router, prefix=API_PREFIX)
app.include_router(investments.router, prefix=API_PREFIX)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Benvenuto in FinConnect API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
