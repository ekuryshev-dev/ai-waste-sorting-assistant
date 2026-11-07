from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from .errors import ClassificationError


class ImageProcessor:
    """Prepare an uploaded image for the 224 x 224 RGB CV model."""

    def __init__(self, size: int = 224):
        self.set_size(size)

    def get_size(self) -> int:
        return self._size

    def set_size(self, value: int) -> None:
        self._size = value

    def prepare(self, data: bytes) -> Image.Image:
        try:
            with Image.open(BytesIO(data)) as source:
                image = source.convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise ClassificationError("The uploaded file is not a valid image", 400) from exc
        size = self.get_size()
        return ImageOps.pad(image, (size, size), method=Image.Resampling.LANCZOS, color="white")
