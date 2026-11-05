import json
import sys
import uuid
from pathlib import Path
from dataclasses import asdict

sys.path.insert(0, str(Path(__file__).parent / "backend" / "src"))

from chat_handler_classes import AssistantService, PromptBuilder
from cv_fallback_classes import ImageFallbackClassifier
from data_handler_classes import ChatRepo, DBManager, RulesRepo
from llm_access_classes import LLMMockClient


def main():
    # To avoid security issues with API keys and to simplify the setup,
    # the AI is mocked, the database is in-memory SQLite and the token is randomly generated.
    # The real system uses OpenAI and a Neon database, and receives the token from the frontend.
    db = DBManager("sqlite://")
    db.create_tables()
    session = next(db.get_db())
    token = uuid.uuid4()


    assistant = AssistantService(
        RulesRepo(session),
        ChatRepo(session, expiry=1, limit=20),
        LLMMockClient("Take used batteries to a collection box."),
        PromptBuilder("You are a recycling assistant."),
    )

    print("\n1) Conversation with AI Assistant:")
    prompt = "Where do batteries go?"
    response = assistant.converse(token, prompt)
    print(prompt)
    print(response)

    print("\n2) Conversation history:")
    history = assistant.get_history(token)
    for message in history:
        print(f"{message.role}: {message.content} - {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n3) Chat clearing:")
    assistant.clear_chat(token)
    if assistant.get_history(token) == []:
        print("Chat cleared successfully.")


    fallback = ImageFallbackClassifier(
        LLMMockClient('{"category": "recyclable", "material": "battery", "instructions": "Take it to a collection box."}'),
        RulesRepo(session),
        PromptBuilder("Classify the item. Reply with JSON only."),
    )

    print("\n4) Image fallback classification:")
    image = b"fake-image-bytes"
    result = fallback.classify(image)
    print("Image bytes sent.")
    print(f"Classification result:\n{json.dumps(asdict(result), indent=2)}")

    print("\n5) Getters and setters:")
    print("Setting and getting the maximum classification retries value.")
    fallback.max_retries = 3
    print(f"fallback.max_retries = {fallback.max_retries}")


if __name__ == "__main__":
    print("\n\nAssistant Subsystem Demo.")
    main()
    print("\n")