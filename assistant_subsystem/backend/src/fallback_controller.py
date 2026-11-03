from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import BaseModel
from dependencies import get_cv_service
from data_handler_classes import Category

router = APIRouter(prefix="/fallback", tags=["fallback"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 10 * 1024 * 1024


class FallbackOut(BaseModel):
    category: Category
    material: str | None = None
    instructions: str | None = None


@router.post("/classify", response_model=FallbackOut)
def classify(image: UploadFile, region: str | None = Form(None), service = Depends(get_cv_service)):
    if image.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG or WebP images are accepted.")
    data = image.file.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="The image is larger than 10 MB.")
    return service.classify(data, image.content_type, region)