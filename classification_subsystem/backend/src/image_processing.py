from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from .errors import InvalidImageError


class ImageProcessor:
    ALLOWED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}

    def __init__(self, max_bytes: int = 10 * 1024 * 1024):
        self.max_bytes = max_bytes

    @property
    def max_bytes(self) -> int:
        return self._max_bytes

    @max_bytes.setter
    def max_bytes(self, value: int) -> None:
        if value <= 0:
            raise ValueError("max_bytes must be positive")
        self._max_bytes = value

    def prepare(self, data: bytes, mime_type: str) -> Image.Image:
        if not data or len(data) > self.max_bytes:
            raise InvalidImageError("Image is empty or larger than 10 MB")
        if mime_type not in self.ALLOWED_FORMATS.values():
            raise InvalidImageError("Only JPEG, PNG and WebP images are accepted")
        try:
            with Image.open(BytesIO(data)) as source:
                if self.ALLOWED_FORMATS.get(source.format) != mime_type:
                    raise InvalidImageError("Image content does not match its MIME type")
                image = ImageOps.exif_transpose(source).convert("RGB")
                return ImageOps.pad(
                    image, (224, 224), method=Image.Resampling.LANCZOS, color="white"
                )
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise InvalidImageError("Image cannot be decoded") from exc
