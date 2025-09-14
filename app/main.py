from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import init_db
from .twilio_routes import router as voice_router
from .ws_handler import router as ws_router

app = FastAPI(title="Dash Movers Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(voice_router)
app.include_router(ws_router)

@app.on_event("startup")
def _startup():
    init_db()
