from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.settings import settings

from models.database import Base, engine

import models

from v1.api import api_router


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def health_check():
    return {
        "status": "success",
        "message": "Finance App Running"
    }