from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError

from member.models import Member
from .models import Diary, DiaryTextBox
from .serializers import (DiaryDetailSerializer, DiaryListSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryTextBoxCreateSerializer,
                          DiaryStickerCreateSerializer, DiaryTextBoxSerializer)
from harucalendar.models import Harucalendar
from harucalendar.serializer import HarucalendarCreateSerializer
from .utils import extract_top_keywords, generate_sticker_images
from botocore.exceptions import NoCredentialsError
import boto3
import uuid
import time
import requests

from .swaggerserializer import DiaryGetRequestSerializer, DiaryGetResponseSerializer, DiaryLinkGetResponseSerializer, \
    DiaryTextBoxPutRequestSerializer, DiaryTextBoxPutResponseSerializer


# Create your views here.

class Diaries(APIView):
    # 일기장 조회
    @swagger_auto_schema(query_serializer=DiaryGetRequestSerializer, responses={200: DiaryGetResponseSerializer})
    def get(self, request, diary_id):
        found_diary = get_object_or_404(Diary, diary_id=diary_id)

        try:
            serialized_diary = DiaryDetailSerializer(found_diary).data
            return Response(status=status.HTTP_200_OK, data=serialized_diary)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    #만약 쿠키가 있다면 캘린더 아이디만 받게 ??

    # 일기장 생성
    @staticmethod
    def post(request):
        # 쿠키로 받아서 쓸거임 claendar id, member-id
        calendar_id = request.data.get('calendar_id')
        member_id = request.data.get('member_id')
        # 쿠키 세션을 받아와서 켈린더,맴버 아이디를 찾아온다음,
        # 날짜에서 연월만 추출

        year_month_day = request.data.get('diary_date')  # 이건 받아서 쓸거임

        # 캘린더가 없을때
        if calendar_id is None:
            member_instance = get_object_or_404(Member, member_id=member_id)  # 멤버 인스턴스 받아오기
            calendar_serializer = HarucalendarCreateSerializer(data={'year_month_day': year_month_day})  # 캘린더 생성
            if calendar_serializer.is_valid():
                calendar_serializer.save(member_id=member_instance)  # 캘린더 생성 완료
                # 캘린더 생성 후 일기장 저장.
                new_calendar_pk = calendar_serializer.instance.pk
                new_calendar_instance = get_object_or_404(Harucalendar, calendar=new_calendar_pk)
                diary_serializer = DiaryCreateSerializer(data=request.data)
                if diary_serializer.is_valid():
                    diary_serializer.save(calendar=new_calendar_instance)
                    return Response(diary_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)


            else:
                return Response({'errors': '데이터 값이 유효하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)


        # 캘린더가 있을떄(diary_id가 있을떄)
        else:
            calendar_instance = get_object_or_404(Harucalendar, calendar=request.data.get('calendar_id'))
            calendar_duplication = Harucalendar.objects.filter(year_month_day=request.data.get('diary_date'))
            if calendar_duplication:
                return Response({'error': '해당일에 이미 일기가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            diary_serializer = DiaryCreateSerializer(data=request.data)
            if diary_serializer.is_valid():
                diary_serializer.save(calendar=calendar_instance)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(diary_serializer.data, status=status.HTTP_400_BAD_REQUEST)

    # 일기장 최종 저장


# 일기장 링크공유
class DiaryManager(APIView):
    @swagger_auto_schema(responses={200: DiaryLinkGetResponseSerializer})
    def get(self, request, diary_id):

        found_diary = Diary.objects.get(diary_id=diary_id)

        try:
            sns_link = DiarySnsLinkSerializer(found_diary)
            return Response(status=status.HTTP_200_OK, data=sns_link.data)
        except ObjectDoesNotExist:
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DiaryTextBoxManager(APIView):
    @swagger_auto_schema(
        request_body=DiaryTextBoxPutRequestSerializer,  # YourSerializer는 사용자 정의 시리얼라이저입니다.
        responses={200: 'DiaryTextBoxPutResponseSerializer'},
        operation_description="This is your PUT method description."
    )
    def put(self, request):
        diary_id = request.data.get('diary_id')
        if diary_id is None:
            return Response({"error": "diary does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data is None:
            return Response({"error": "diary data does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:

            diary_instance = get_object_or_404(Diary, diary_id=diary_id)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

        textboxes_data = request.data.get('textboxes', [])
        stickers_data = request.data.get('stickers', [])
        try:
            for textboxes_data in textboxes_data:
                textbox_serializer = DiaryTextBoxCreateSerializer(data=textboxes_data)
                if textbox_serializer.is_valid():
                    textbox_serializer.save(diary=diary_instance)
            for sticker_data in stickers_data:
                sticker_serializer = DiaryStickerCreateSerializer(data=sticker_data)
                if sticker_serializer.is_valid():
                    sticker_serializer.save(diary=diary_instance)
            return Response({'code': 'D001', 'status': '201', 'message': '일기장 저장 성공!'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)


    '''
    @swagger_auto_schema(query_serializer=DiaryTextBoxPostRequestSerializer,responses={200:DiaryTextBoxPostResponseSerializer})
    def post(self, request):
        diary_instance = get_object_or_404(Diary, diary_id=request.query_params.get('diary_id'))
        content = request.query_params.get('content')
        diarytextbox_serializer = DiaryTextBoxCreateSerializer(data={'content': content})

        if diarytextbox_serializer.is_valid():
            diarytextbox_pk = diarytextbox_serializer.save(diary=diary_instance)
            return Response({'textbox_id': diarytextbox_pk.pk}, status=status.HTTP_201_CREATED)

        else: 
            return Response(status=status.HTTP_400_BAD_REQUEST)
    '''


class DiaryStickerManager(APIView):

    def post(self, request, format=None):
        start = time.time()
        print(request.POST.get('_content'))
        try:
            content = request.POST.get('_content')

            # DiaryTextBox 모델에 데이터 저장
            # diary_text_box = DiaryTextBox.objects.create(content=content)

            # 일기 내용에서 상위 3개 키워드 추출
            top_keywords = extract_top_keywords(content)

            # 상위 키워드로 DALL-E API 호출하여 스티커 이미지 생성
            sticker_image_urls = generate_sticker_images(top_keywords)

            # 이미지 업로드 및 URL 반환
            uploaded_image_urls = []
            for keyword, sticker_url in sticker_image_urls.items():
                response = self.upload_image_to_s3(sticker_url, keyword)
                uploaded_image_urls.append(response['image_url'])

            response_data = {
                'code': 'D001',
                'status': '201',
                'message': '이미지 생성 성공',
                'data': {
                    'sticker_image_urls': uploaded_image_urls,
                }
            }
            end = time.time()
            print(f"{end - start:.5f} sec")
            return Response(response_data, status=status.HTTP_201_CREATED)
        except NoCredentialsError:
            return Response({"message": "AWS credentials not available."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            response_data = {
                'code': 'D001',
                'status': '500',
                'message': f'에러 발생: {str(e)}',
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def upload_image_to_s3(self, image_data, keyword):
        try:
            # AWS S3 연결
            s3_client = boto3.client('s3', region_name='ap-northeast-2')

            # 파일 이름 설정 (여기서는 UUID 사용)
            file_name = f"{keyword.replace(' ', '_')}_{str(uuid.uuid4())}.png"

            # S3 버킷에 파일 업로드
            s3_client.put_object(
                Body=image_data,
                Bucket='harudiary-sticker-bucket',
                Key=file_name,
                ContentType='image/png',
            )

            # 업로드된 이미지의 S3 URL 반환
            image_url = f"https://harudiary-sticker-bucket.s3.amazonaws.com/{file_name}"

            return {
                'status': 'success',
                'message': '이미지 업로드 성공',
                'image_url': image_url,
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'이미지 업로드 에러: {str(e)}',
            }
