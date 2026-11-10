import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Session
from chat_handler_classes import AssistantService, PromptBuilder
from cv_fallback_classes import ImageFallbackClassifier
from data_handler_classes import ChatRepo, DBManager, RulesRepo
from llm_access_classes import LLMMockClient, OpenAIClient


load_dotenv()

db_manager = DBManager(os.getenv("DATABASE_URL", "sqlite://"))
api_key = os.getenv("OPENAI_API")
sys_prompt = (Path(__file__).resolve().parent.parent / "sysprompt.txt").read_text(encoding="utf-8")
cv_sys_prompt = (Path(__file__).resolve().parent.parent / "cv_sysprompt.txt").read_text(encoding="utf-8")

if not api_key:
    logging.getLogger(__name__).warning("OPENAI_API is not set, using the mock AI client")


def get_ai_client(mock_reply):
    if api_key:
        return OpenAIClient(model="gpt-6-luna", timeout=20, api=api_key)
    return LLMMockClient(mock_reply)


def get_service(session: Session = Depends(db_manager.get_db)):
    return AssistantService(
        RulesRepo(session),
        ChatRepo(session=session, expiry=1, limit=20),
        get_ai_client("Mock reply. Set OPENAI_API to talk to the real assistant."),
        PromptBuilder(sys_prompt),
    )


def get_cv_service(session: Session = Depends(db_manager.get_db)):
    return ImageFallbackClassifier(
        get_ai_client('{"category": "recyclable", "material": "mock item", "instructions": "Mock result. Set OPENAI_API for real classification."}'),
        RulesRepo(session),
        PromptBuilder(cv_sys_prompt),
    )