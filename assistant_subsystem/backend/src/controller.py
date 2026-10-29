from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from chat_handler_classes import AssistantService
from dependencies import get_service


router = APIRouter(prefix="/chat", tags=["chat"])


class DTOin(BaseModel):
    text: str = Field(min_length=1, max_length=500)

class DTOout(BaseModel):
    role: str
    content: str


@router.post("/{token}", response_model=DTOout)
def converse(token: UUID, body: DTOin, service = Depends(get_service)):
    return {"role": "assistant", "content": service.converse(token, body.text)}


@router.get("/{token}", response_model=list[DTOout])
def get_history(token: UUID, service = Depends(get_service)):
    return service.get_history(token)


@router.delete("/{token}", status_code=204)
def clear_chat(token: UUID, service = Depends(get_service)):
    service.clear_chat(token)