from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from member.models import Member
from .models import Diary
from .serializers import (DiaryDetailSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryTextBoxCreateSerializer,
                          DiaryStickerCreateSerializer, DiaryUpdateSerializer)
from harucalendar.models import Harucalendar
from harucalendar.serializer import HarucalendarCreateSerializer
from .utils import extract_top_keywords, generate_sticker_images
from botocore.exceptions import NoCredentialsError
import boto3
import uuid
import time

from .swaggerserializer import DiaryGetResponseSerializer, DiaryLinkGetResponseSerializer, \
    DiaryTextBoxPutRequestSerializer, DiaryStickerRequestSerializer, \
    DiaryStickerGetResponseSerializer, SwaggerDiaryCreateRequestSerializer, SwaggerDiaryCreateResponseSerializer


# Create your views here.

class Diaries(APIView):
    # 일기장 조회

    @swagger_auto_schema(
        operation_description="일기에 연동 된 텍스트박스,스티커 등등 출력<br>1.해당달에 존재 하는 전반적인 일기 목록은 캘린더 조회에서 확인<br> 2.일기의 세부 내용(스티커,텍스트박스 등) 출력",
        operation_summary="일기 조회",
        responses={200: DiaryGetResponseSerializer}
    )
    def get(self, request, diary_id):
        found_diary = get_object_or_404(Diary, diary_id=diary_id)

        try:
            serialized_diary = DiaryDetailSerializer(found_diary).data

            return Response(status=status.HTTP_200_OK, data=serialized_diary)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(request_body=SwaggerDiaryCreateRequestSerializer, responses={200: SwaggerDiaryCreateResponseSerializer})
    def post(request):
        # 쿠키로 받아서 쓸거임 claendar id, member-id
        calendar_id = request.session.get('calendar_id')
        member_id = request.session.get('member_id')

        if member_id is None:
            return Response({'error': '로그인이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
        diary_date = request.data.get('diary_date')

        if calendar_id is None:
            member_instance = get_object_or_404(Member, member_id=member_id)
            calendar_serializer = HarucalendarCreateSerializer(data={'year_month': year_month})

            if calendar_serializer.is_valid():
                calendar_instance = calendar_serializer.save(member=member_instance)

                diary_serializer = DiaryCreateSerializer(data=request.data)

                if diary_serializer.is_valid():
                    diary_serializer.save(calendar=calendar_instance)
                    return Response({'calendar_id': calendar_instance.pk, 'diary_data': diary_serializer.data},
                                    status=status.HTTP_200_OK)
                else:
                    return Response({'errors': 'Invalid data for diary'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'errors': 'Invalid data for calendar'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            calendar_instance = get_object_or_404(Harucalendar, calendar_id=calendar_id)
            diary_duplication = Diary.objects.filter(calendar=calendar_id,year_month=year_month,day=day)

            if diary_duplication:
                return Response({'error': '해당 날짜에 다이어리가 있습니다.'},
                                status=status.HTTP_400_BAD_REQUEST)
              
            diary_serializer = DiaryCreateSerializer(data=diary_data)
            if diary_serializer.is_valid():
                diary_instance = diary_serializer.save(calendar=calendar_instance)
                data = {"sns_link": f"{request.get_host()}/ws/{diary_instance.diary_id}?type=member&member={member_id}"}
                diary_update_serializer = DiaryUpdateSerializer(diary_instance, data=data)
                if diary_update_serializer.is_valid():
                    diary_update_serializer.save()
                    return Response(diary_update_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'snsLink가 유효하지 않습니다.'})

        if calendar_id is not None:
            diary_exist = Diary.objects.filter(calendar=calendar_id, diary_date=diary_date).exists()
            if diary_exist:
                return Response({'error': '해당 일에 이미 일기가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            diary_data = {'diary_bg_url': "found_static_url", 'diary_date': diary_date}
            diary_serializer = DiaryCreateSerializer(data=diary_data)
            if diary_serializer.is_valid():
                diary_instance = diary_serializer.save(calendar_id=calendar_id)
                data = {"sns_link": f"{request.get_host()}/ws/{diary_instance.diary_id}?type=member&member={member_id}"}
                diary_update_serializer = DiaryUpdateSerializer(diary_instance, data=data)
                if diary_update_serializer.is_valid():
                    diary_update_serializer.save()
                    return Response(diary_update_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'snsLink가 유효하지 않습니다.'})
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '일기 생성 데이터가 유효하지 않습니다..'})


def request_manager(request):
    diary_bg_id = request.data.delete('diary_bg_id')
    ### 일기장 배경 조회해오기 ###
    request.data['diary_bg_url'] = "found_static_url"
    return request


            # if diary_instance is None:
            #     print('diary_instance is None')

                # 캘린더 생성 완료
                # 캘린더 생성 후 일기장 저장.
        #
        #         # found_static = get_object_or_404(StaticBgImage, static_id=request.data.get('static_bg_id'))
        #         request.data['diary_bg_url'] = "found_static_url"
        #         # request.data['sns_link'] = "nazoongeh"
        #
        #         diary_serializera = DiaryCreateSerializer(data=request.data)
        #         if diary_serializera.is_valid():
        #             diary_serializera.save(calendar=calendar_instance)
        #         else:
        #             return Response(status=status.HTTP_400_BAD_REQUEST)
        #         diary_id = diary_serializera.data['diary_id']
        #         request.session['member_id'] = member_id
        #         f"{request.get_host()}/ws/{diary_id}?type=guest&guest={member_id}"
        #         return Response(diary_serializera.data, status=status.HTTP_200_OK)
        #
        #     else:
        #         return Response({'errors': '데이터 값이 유효하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        #
        #
        # # 캘린더가 있을떄(diary_id가 있을떄)
        # else:
        #     calendar_instance = get_object_or_404(Harucalendar, calendar=request.data.get('calendar_id'))
        #     calendar_duplication = Harucalendar.objects.filter(year_month_day=request.data.get('diary_date'))
        #     if calendar_duplication:
        #         return Response({'error': '해당일에 이미 일기가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        #     diary_serializer = DiaryCreateSerializer(data=request.data)
        #     if diary_serializer.is_valid():
        #         diary_serializer.save(calendar=calendar_instance)
        #     else:
        #         return Response(diary_serializer.data, status=status.HTTP_400_BAD_REQUEST)


    # 일기장 최종 저장

# 일기장 링크공유
class DiaryManager(APIView):
    @swagger_auto_schema(
        responses={200: DiaryLinkGetResponseSerializer})
    def get(self, request, diary_id):

        found_diary = Diary.objects.get(diary_id=diary_id)

        try:
            sns_link = DiarySnsLinkSerializer(found_diary)
            return Response(status=status.HTTP_200_OK, data=sns_link.data)
        except ObjectDoesNotExist:
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DiariesPut(APIView):
    @swagger_auto_schema(operation_description="일기 최종 저장",
                         operation_summary="기존 만들어진 일기에 일기 텍스트 박스 및 스티커 정보 저장",
                         request_body=DiaryTextBoxPutRequestSerializer,
                         responses={200: 'DiaryTextBoxPutResponseSerializer'},

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
        textboxs_data = request.data.get('textboxs', [])
        stickers_data = request.data.get('stickers', [])
        try:
            for sticker_data in stickers_data:
                sticker_serializer = DiaryStickerCreateSerializer(data=sticker_data)
                if sticker_serializer.is_valid():
                    sticker_serializer.save(diary=diary_instance)
                else:
                    print(sticker_serializer.errors)
            for textbox_data in textboxs_data:
                textbox_serializer = DiaryTextBoxCreateSerializer(data=textbox_data)
                if textbox_serializer.is_valid():
                    textbox_serializer.save(diary=diary_instance)
                else:
                    print(textbox_serializer.errors)

            return Response({'code': 'D001', 'status': '201', 'message': '일기장 저장 성공!'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)


# 일기장 링크공유
class DiaryManager(APIView):
    @swagger_auto_schema(
        responses={200: DiaryLinkGetResponseSerializer})
    def get(self, request, diary_id):

        found_diary = Diary.objects.get(diary_id=diary_id)
        print('dddd')
        try:
            sns_link = DiarySnsLinkSerializer(found_diary)
            return Response(status=status.HTTP_200_OK, data=sns_link.data)
        except ObjectDoesNotExist:
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DiaryTextBoxManager(APIView):
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
    @swagger_auto_schema(request_body=DiaryStickerRequestSerializer,
                         responses={201: DiaryStickerGetResponseSerializer})
    def post(self, request, format=None):
        start = time.time()
        print(request.data.get('content'))
        try:
            content = request.data.get('content')

            # DiaryTextBox 모델에 데이터 저장
            # diary_text_box = DiaryTextBox.objects.create(content=content)

            # 일기 내용에서 상위 3개 키워드 추출
            top_keywords = extract_top_keywords(content)
            print(top_keywords)
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
            return Response(response_data, status=201)
        except NoCredentialsError:
            return Response({"message": "AWS credentials not available."}, status=500)
        except Exception as e:
            response_data = {
                'code': 'D001',
                'status': '500',
                'message': f'에러 발생: {str(e)}',
            }
            return Response(response_data, status=500)

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
