from data_handler_classes import DBManager, RulesRepo, ChatRepo
from chat_handler_classes import AssistantService, PromptBuilder
from llm_access_classes import OpenAIClient
import os
from dotenv import load_dotenv
from sqlmodel import Session
from fastapi import Depends
from pathlib import Path
from cv_fallback_classes import ImageFallbackClassifier


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

db_manager = DBManager(os.getenv("DATABASE_URL", "sqlite://"))
sys_prompt = (Path(__file__).resolve().parent.parent / "sysprompt.txt").read_text(encoding="utf-8")
cv_sys_prompt = (Path(__file__).resolve().parent.parent / "cv_sysprompt.txt").read_text(encoding="utf-8")


def get_service(session: Session = Depends(db_manager.get_db)):
    return AssistantService(
        RulesRepo(session),
        ChatRepo(session=session, expiry=1, limit=20),
        OpenAIClient(model="gpt-6-luna", timeout=20, api=os.getenv("OPENAI_API")),
        PromptBuilder(sys_prompt),
    )


def get_cv_service(session: Session = Depends(db_manager.get_db)):
    return ImageFallbackClassifier(
        OpenAIClient(model="gpt-6-luna", timeout=20, api=os.getenv("OPENAI_API")),
        RulesRepo(session),
        PromptBuilder(cv_sys_prompt),
    )