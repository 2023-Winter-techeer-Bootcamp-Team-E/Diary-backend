import boto3
from collections import Counter
from openai import OpenAI
import requests
from PIL import Image
from io import BytesIO
from rembg import remove

def extract_top_keywords(diary_text):
    comprehend_client = boto3.client('comprehend', region_name='ap-northeast-2')

    cleaned_text = preprocess_diary_text(diary_text)

    response = comprehend_client.detect_key_phrases(
        Text=cleaned_text,
        LanguageCode='ko'
    )

    keywords = [phrase['Text'] for phrase in response['KeyPhrases']]
    stopwords = get_korean_stopwords()
    filtered_keywords = [keyword for keyword in keywords if keyword not in stopwords]
    keyword_counts = Counter(filtered_keywords)
    top_keywords = keyword_counts.most_common(2)

    return [keyword[0] for keyword in top_keywords]

def preprocess_diary_text(diary_text):
    cleaned_text = ''.join(char for char in diary_text if char.isalnum() or char.isspace())
    return cleaned_text

def get_korean_stopwords():
    stopwords = [
        "나", "오늘", "우리", "저희", "따라", "의해", "을", "를", "에", "의", "가", "으로", "로", "에게", "뿐이야",
        "여서", "그리고"
    ]
    return stopwords

def generate_sticker_image(keyword):
    client = OpenAI(api_key="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")

    response = client.images.generate(
        model="dall-e-3",
        prompt=f"{keyword} 스티커",
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    return image_url

def remove_background(image_data):
    with Image.open(BytesIO(image_data)) as img:
        #이미지 크기 조절
        img = img.resize((300, 300))

        new_img = remove(img)

        output_buffer = BytesIO()

        new_img.save(output_buffer, format="PNG")
        output_data = output_buffer.getvalue()

    return output_data


def generate_sticker_images(keywords):
    sticker_image_urls = {}

    for keyword in keywords:
        sticker_image_url = generate_sticker_image(keyword)

        response = requests.get(sticker_image_url)
        image_data = response.content

        output_data = remove_background(image_data)

        with open(f"{keyword}_sticker_image_no_bg.png", "wb") as f:
            f.write(output_data)

        sticker_image_urls[keyword] = f"{keyword}_sticker_image_no_bg.png"
        print(f"스티커 이미지 파일 경로 ({keyword}): {sticker_image_urls[keyword]}")

    return sticker_image_urls
