from openai import OpenAI
import base64
from pathlib import Path

client = OpenAI()

class ImageService:

    def generate_image(self, prompt, output_path):
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1536x1024"
        )

        image = base64.b64decode(result.data[0].b64_json)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image)

        return output_path