from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dependencies import db_manager
from controller import router as chat_router
from errors import LLMError


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


@app.exception_handler(LLMError)
async def llm_error_handler(request: Request, exc: LLMError):
    return JSONResponse(status_code=502, content={"detail": "The assistant is unavailable right now. Please try again."})


@app.get("/health")
def health():
    return {"status": "ok"}