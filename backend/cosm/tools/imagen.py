from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from typing import List

from cosm.settings import settings

client = genai.Client(api_key=settings.GOOGLE_API_KEY)


def generate_logo(prompt: str) -> List[str]:
    response = client.models.generate_images(
        model="imagen-3.0-generate-002",
        prompt=prompt,
        config=types.GenerateImagesConfig(
            number_of_images=2,
        ),
    )
    for generated_image in response.generated_images:
        image = Image.open(BytesIO(generated_image.image.image_bytes))
        image.show()
