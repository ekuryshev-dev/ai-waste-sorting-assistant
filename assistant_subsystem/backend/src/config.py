from data_handler_classes import DBManager
import os
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
ai_api = os.getenv("OPENAI_API")
ai_model = os.getenv("OPENAI_MODEL")
ai_timeout = int(os.getenv("OPENAI_TIMEOUT"))
message_limit = int(os.getenv("MESSAGE_LIMIT"))
chat_expiry = int(os.getenv("CHAT_EXPIRY"))

db_manager = DBManager(db_url)
db_manager.create_tables()