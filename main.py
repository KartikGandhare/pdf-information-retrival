from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Financial Loss Analysis API",
    description="Agentic AI system for financial analysis and recommendations",
    version="1.0.0",
)


app.include_router(router)