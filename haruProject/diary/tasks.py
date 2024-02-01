# tasks.py
from celery import shared_task
from openai import OpenAI
from PIL import Image
from io import BytesIO
from rembg import remove
from config.settings import DALLE_API_KEY
import boto3
import uuid

@shared_task
def generate_sticker_image(keyword):

    client = OpenAI(api_key=DALLE_API_KEY)
    response = client.images.generate(
        model="dall-e-3",
        prompt=f"Single {keyword} object that is cute, and illustrative feel. This object must not contain any content, text or multi characters. Save this within a circular thin frame.",
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
        img = img.resize((300, 300))

        new_img = remove(img)
        output_buffer = BytesIO()
        new_img.save(output_buffer, format="PNG")
        output_data = output_buffer.getvalue()

    return output_data
@shared_task
def upload_image_to_s3(image_data, keyword):
    try:
            # AWS S3 연결
        s3_client = boto3.client('s3', region_name='ap-northeast-2')
        print("s3 업로드1")
            # 파일 이름 설정 (여기서는 UUID 사용)
        file_name = f"{keyword.replace(' ', '_')}_{str(uuid.uuid4())}.png"

            # S3 버킷에 파일 업로드
        s3_client.put_object(
                Body=image_data,
                Bucket='harudiary-sticker-bucket',
                Key=file_name,
                ContentType='image/png',
            )
        print("s3 압로드2")
        # 업로드된 이미지의 S3 URL 반환
        image_url = f"https://harudiary-sticker-bucket.s3.amazonaws.com/{file_name}"
        print("s3 압로드 성공")
        return {'image_url': image_url}

    except Exception as e:
        return {
                'status': 'error',
                'message': f'이미지 업로드 에러: {str(e)}',
            }


