from data_handler_classes import DBManager, RulesRepo, ChatRepo
from chat_handler_classes import AssistantService, PromptBuilder
from llm_access_classes import OpenAIClient
import os
from dotenv import load_dotenv
from sqlmodel import Session
from fastapi import Depends

load_dotenv()
db_url = os.getenv("DATABASE_URL")
ai_api = os.getenv("OPENAI_API")
ai_model = os.getenv("OPENAI_MODEL")
ai_timeout = int(os.getenv("OPENAI_TIMEOUT"))
message_limit = int(os.getenv("MESSAGE_LIMIT"))
chat_expiry = int(os.getenv("CHAT_EXPIRY"))
sys_prompt = os.getenv("SYSTEM_PROMPT")

db_manager = DBManager(db_url)
db_manager.create_tables()

def get_service(session: Session = Depends(db_manager.get_db)):
    return AssistantService(
        RulesRepo(session),
        ChatRepo(session, chat_expiry, message_limit),
        OpenAIClient(ai_model, ai_timeout, ai_api),
        PromptBuilder(sys_prompt),
    )