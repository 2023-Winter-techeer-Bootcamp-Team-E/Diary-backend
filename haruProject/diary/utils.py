import boto3
from collections import Counter
import requests
from .tasks import generate_sticker_image, remove_background


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
        "여서", "그리고", "이여서"
    ]
    return stopwords


def generate_sticker_images(keywords):

    sticker_image_urls = {}

    tasks = []
    for keyword in keywords:
        task = generate_sticker_image.delay(keyword)
        tasks.append((keyword, task))

    for keyword, task in tasks:

        result = task.get()  # 대기하면서 결과 가져오기

        response = requests.get(result)
        image_data = response.content
        output_data = remove_background.delay(image_data).get()

        sticker_image_urls[keyword] = output_data

    return sticker_image_urls
