from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dependencies import db_manager
from controller import router as chat_router
from errors import LLMError
import logging
from fallback_controller import router as fallback_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_manager.create_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # the Vite dev server; add the Netlify URL later
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(fallback_router)


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    logging.getLogger(__name__).error("LLM error: %s", exc)
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.user_message})


@app.get("/health")
def health():
    return {"status": "ok"}