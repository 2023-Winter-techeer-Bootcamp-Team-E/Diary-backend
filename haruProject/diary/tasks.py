# tasks.py
from celery import shared_task
from openai import OpenAI
from PIL import Image
from io import BytesIO
from rembg import remove
from config.settings import DALLE_API_KEY


@shared_task
def generate_sticker_image(keyword):
    client = OpenAI(api_key=DALLE_API_KEY)

    response = client.images.generate(
        model="dall-e-3",
        prompt=f"일러스트 느낌의 {keyword} 스티커만 그려줘",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    return image_url


@shared_task
def remove_background(image_data):
    with Image.open(BytesIO(image_data)) as img:
        # 이미지 크기 조절 - 프론트엔드와 API연결 후 로딩시간 체크한 뒤에 이미지 사이즈 조절하는 걸로
        # img = img.resize((300, 300))

        new_img = remove(img)
        output_buffer = BytesIO()
        new_img.save(output_buffer, format="PNG")
        output_data = output_buffer.getvalue()

    return output_data