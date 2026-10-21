
import base64
import logging
import os
from pathlib import Path
from threading import Lock

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class ImageService:
    """Centralized OpenAI image generation service."""

    _client = None
    _client_lock = Lock()

    def __init__(self, timeout: float = 120.0):
        self.timeout = timeout

    def _get_client(self):
        """Create the API client only when an image is requested."""
        if ImageService._client is None:
            with ImageService._client_lock:
                if ImageService._client is None:
                    api_key = os.getenv("OPENAI_API_KEY")

                    if not api_key:
                        raise RuntimeError(
                            "OPENAI_API_KEY is missing. "
                            "Check the backend .env configuration."
                        )

                    ImageService._client = OpenAI(
                        api_key=api_key,
                        timeout=self.timeout,
                        max_retries=2,
                    )

        return ImageService._client

    def generate_image(self, prompt: str, output_path) -> str:
        """
        Generate an image and save it locally.

        Returns the saved file path.
        Raises an exception on failure so the calling workflow
        can log the failure and decide whether to continue.
        """
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Image prompt cannot be empty.")

        destination = Path(output_path).resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)

        client = self._get_client()

        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt.strip(),
            size="1536x1024",
        )

        if not result.data or not result.data[0].b64_json:
            raise RuntimeError("The image API returned no image data.")

        image_bytes = base64.b64decode(
            result.data[0].b64_json,
            validate=True,
        )

        if not image_bytes:
            raise RuntimeError("The generated image file is empty.")

        destination.write_bytes(image_bytes)

        logger.info("Generated image saved: %s", destination)
        return str(destination)
