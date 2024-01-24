from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import member
from member.models import Member
from .models import Diary
from .serializers import (DiaryDetailSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryTextBoxCreateSerializer,
                          DiaryStickerCreateSerializer, DiaryUpdateSerializer)
from harucalendar.serializer import HarucalendarCreateSerializer
from .utils import extract_top_keywords, generate_sticker_images
from botocore.exceptions import NoCredentialsError
import boto3
import uuid
import time


from .swaggerserializer import DiaryGetResponseSerializer, DiaryLinkGetResponseSerializer, \
    DiaryTextBoxPutRequestSerializer, DiaryStickerRequestSerializer, \
    DiaryStickerGetResponseSerializer, SwaggerDiaryCreateRequestSerializer, SwaggerDiaryCreateResponseSerializer, \
    DiaryGetRequestSerializer, DiaryLinkRequestSerializer, DiaryTextBoxPutResponseSerializer

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Create your views here.

class Diaries(APIView):
    # 일기장 조회
    @swagger_auto_schema(
        operation_description="일기에 연동 된 텍스트박스,스티커 등등 출력<br>1.해당달에 존재 하는 전반적인 일기 목록은 캘린더 조회에서 확인<br> 2.일기의 세부 내용(스티커,텍스트박스 등) 출력",
        operation_summary="일기 조회",
        query_serializer=DiaryGetRequestSerializer,
        responses={200: DiaryGetResponseSerializer}
    )
    def get(self, request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        member_id = request.session.get('member_id')
        nickname = request.session.get('nickname')
        try:
            day = request.GET.get('day') #swagger에서는 GET, postman은 data
            calendar_id = request.session.get('calendar_id')
            found_diary = Diary.objects.get(day=day, calendar_id=calendar_id)
            request.session['diary_id'] = found_diary.diary_id
            serialized_diary = DiaryDetailSerializer(found_diary).data
            logger.info(f'{client_ip}-[{current_time}] "GET", "/diaries" 200  member: {member_id}, nickname: {nickname}, 일기장을 조회하였습니다.. ')
            return Response(status=status.HTTP_200_OK, data=serialized_diary)
        except ObjectDoesNotExist:
            logger.info(f'{client_ip}-[{current_time}] "GET", "/diaries" 404  member: {member_id}, nickname: {nickname}, 일기장이 존재하지 않습니다. ')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    @swagger_auto_schema(
        operation_description="일기 배경지 고르기<br>1.일기배경지 고르기<br> 2.sns링크 반환",
        operation_summary="일기초안 생성(배경지 고르기)",
        request_body=SwaggerDiaryCreateRequestSerializer,
        responses={200: SwaggerDiaryCreateResponseSerializer})
    def post(request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nickname = request.session.get('nickname')
        # calendar_id,year_month,member_id만 세션으로 받고, day만 request로 받을거임
        calendar_id = request.session.get('calendar_id')
        year_month = request.session.get('year_month')
        member_id = request.session.get('member_id')
        day = request.data.get('day')
        diary_bg_id = request.data.get('diary_bg_id')

        if member_id is None:
            logger.info(f'{client_ip}-[{current_time}] "POST", "/diaries" 400  member: {member_id}, nickname: {nickname}, 로그인이 필요합니다. ')
            return Response({'error': '로그인이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        # 캘린더 조회는 했으나 캘린더를 안꾸미고 바로 일기를 작성하는 상남자들을 위한 부분.
        # 캘린더 조회시 calendar_id=null을 받았으나 캘린더를 안꾸며서 캘린더가 안생긴 부류

        if calendar_id is None:
            member_instance = get_object_or_404(Member, member_id=member_id)
            calendar_serializer = HarucalendarCreateSerializer(data={'year_month': year_month})
            if calendar_serializer.is_valid():
                logger.info(f'{client_ip}-[{current_time}] "POST", "/diaries" 200  member: {member_id}, nickname: {nickname}, 캘린더 생성 완료. ')
                calendar_instance = calendar_serializer.save(member=member_instance)
                calendar_id = calendar_instance.calendar_id
                request.session['calendar_id'] = calendar_id  # 캘린더를 만들어주고 session에 calendar_id 최신화.

            else:
                logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 400  member: {member_id}, nickname: {nickname}, 멤버와 캘린더 값이 유효하지 않습니다.')
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '멤버와 캘린더 값이 유효하지 않습니다.'})

            diary_data = {'diary_bg_id': diary_bg_id, 'year_month': year_month, 'day': day}

            diary_serializer = DiaryCreateSerializer(data=diary_data)
            if diary_serializer.is_valid():
                logger.info(f'{client_ip}-[{current_time}] "POST", "/diaries" 200  member: {member_id}, nickname: {nickname}, 일기 생성 완료')
                member_object = Member.objects.get(member_id=member_id)
                diary_instance = diary_serializer.save(calendar=calendar_instance)
                request.session['diary_id'] = diary_instance.diary_id

                sns_link = f"{request.get_host()}/ws/{diary_instance.diary_id}?type=member&member={member_id}"
                data = {"sns_link": sns_link}
                response_data = {
                    "diary_id": diary_instance.diary_id,
                    "diary_bg_id": diary_instance.diary_bg_id,
                    "sns_link": sns_link,
                    "year_month": year_month,
                    "day": day,
                    "nickname": member_object.nickname}
                diary_update_serializer = DiaryUpdateSerializer(diary_instance, data=data)
                if diary_update_serializer.is_valid():
                    diary_update_serializer.save()
                    logger.info(f'{client_ip}-[{current_time}] "POST", "/diaries" 200  member: {member_id}, nickname: {nickname}, 다이어리 저장 완료')
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 400  member: {member_id}, nickname: {nickname}, snsLink가 유효하지 않습니다')
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'snsLink가 유효하지 않습니다.'})

        if calendar_id is not None:
            diary_exist = Diary.objects.filter(calendar=calendar_id, day=day).exists()

            if diary_exist:
                logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 400  member: {member_id}, nickname: {nickname}, 해당 일에 이미 일기가 있습니다.')
                return Response({'error': '해당 일에 이미 일기가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            diary_data = {'diary_bg_id': diary_bg_id, 'year_month': year_month, 'day': day}
            diary_serializer = DiaryCreateSerializer(data=diary_data)
            if diary_serializer.is_valid():
                # calendar_instance = get_object_or_404(Harucalendar, calendar_id=calendar_id)
                member_object = Member.objects.get(member_id=member_id)
                diary_instance = diary_serializer.save(calendar_id=calendar_id)
                request.session['diary_id'] = diary_instance.diary_id


                sns_link = f"{request.get_host()}/ws/{diary_instance.diary_id}?type=member&member={member_id}"
                data = {"sns_link": sns_link}
                response_data = {
                    "diary_id": diary_instance.diary_id,
                    "diary_bg_id": diary_instance.diary_bg_id,
                    "year_month": year_month,
                    "day": day,
                    "nickname": member_object.nickname,
                    "sns_link": sns_link}
                diary_update_serializer = DiaryUpdateSerializer(diary_instance, data=data)
                if diary_update_serializer.is_valid():
                    diary_update_serializer.save()
                    logger.info(f'{client_ip}-[{current_time}] "POST", "/diaries" 200  member: {member_id}, nickname: {nickname}, 일기 생성완료.')
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 400  member: {member_id}, nickname: {nickname}, snsLink가 유효하지 않습니다.')
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'snsLink가 유효하지 않습니다.'})
            else:
                logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 400  member: {member_id}, nickname: {nickname}, 일기 생성 데이터가 유효하지 않습니다.')
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '일기 생성 데이터가 유효하지 않습니다.'})

    def request_manager(request):
        diary_bg_id = request.data.delete('diary_bg_id')
        ### 일기장 배경 조회해오기 ###
        request.data['diary_bg_url'] = "found_static_url"
        return request
        # 일기장 생성


class DiariesSave(APIView):
    @swagger_auto_schema(operation_description="일기 최종 저장",
                         operation_summary="기존 만들어진 일기에 일기 텍스트 박스 및 스티커 정보 저장",
                         request_body=DiaryTextBoxPutRequestSerializer,
                         responses={200: DiaryTextBoxPutResponseSerializer},
                         )
    def put(self, request): #캘린더 아디랑
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nickname = request.session.get('nickname')
        member_id = request.session.get('member_id')
        diary_id = request.session.get('diary_id')
        if diary_id is None:
            logger.error(f'{client_ip}-[{current_time}] "PUT", "/diaries" 400  member: {member_id}, nickname: {nickname}, 일기가 없습니다.')
            return Response({"error": "diary does not exist"}, status=status.status.HTTP_404_NOT_FOUND)
        if request.data is None:
            logger.error(f'{client_ip}-[{current_time}] "PUT", "/diaries" 400  member: {member_id}, nickname: {nickname}, 일기에 들어 갈 데이터가 없습니다.')
            return Response({"error": "diary data does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            diary_instance = get_object_or_404(Diary, diary_id=diary_id)
        except ObjectDoesNotExist:
            logger.error(f'{client_ip}-[{current_time}] "PUT", "/diaries" 404  member: {member_id}, nickname: {nickname}, 일기가 없습니다.')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        textboxs_data = request.data.get('textboxs', [])
        stickers_data = request.data.get('stickers', [])
        try:
            for sticker_data in stickers_data:
                sticker_serializer = DiaryStickerCreateSerializer(data=sticker_data)
                if sticker_serializer.is_valid():
                    sticker_serializer.save(diary=diary_instance)
                else:
                    Response({"error": "sticker error"}, status=status.HTTP_404_NOT_FOUND)
            for textbox_data in textboxs_data:
                textbox_serializer = DiaryTextBoxCreateSerializer(data=textbox_data)
                if textbox_serializer.is_valid():
                    textbox_serializer.save(diary=diary_instance)
                else:
                    Response({"error": "textbox error"}, status=status.HTTP_404_NOT_FOUND)
            logger.info(f'{client_ip}-[{current_time}] "PUT", "/diaries" 201  member: {member_id}, nickname: {nickname}, 일기 저장 성공.')
            return Response({'code': 'D001', 'status': '201', 'message': '일기장 저장 성공!'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.error(f'{client_ip}-[{current_time}] "PUT", "/diaries" 404  member: {member_id}, nickname: {nickname}, 일기가 존재하지 않습니다.')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)


# class DiariesPost(APIView):
# 일기장 생성

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


# 일기장 최종 저장


# 일기장 링크공유
class DiaryManager(APIView):
    @staticmethod
    @swagger_auto_schema(operation_summary="작성중인 일기 링크 조회",
                         operation_description="작성중인 일기의 링크 및 diary_id, day, nickname, sns_lin 반환",
                         query_serializer=DiaryLinkRequestSerializer,
                         responses={200: DiaryLinkGetResponseSerializer})
    def get(request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        nickname = request.session.get('nickname')
        calendar_id = request.session.get('calendar_id')
        member_id = request.session.get('member_id')
        day = request.GET.get('day')

        try:
            found_diary = Diary.objects.get(day=day, calendar_id=calendar_id)
            member_instance = Member.objects.get(member_id=member_id)
            sns_link = DiarySnsLinkSerializer(found_diary).data['sns_link']
            response_data = {
                'diary_id': found_diary.diary_id,
                'year_month': found_diary.year_month,
                'day': found_diary.day,
                'nickname': member_instance.nickname,
                'sns_link': sns_link
            }
            logger.info(f'{client_ip}-[{current_time}] "GET", "/diaries" 200  member: {member_id}, nickname: {nickname}, snslink 조회완료: {sns_link}.')
            return Response(response_data, status=200)
        except ObjectDoesNotExist:
            logger.error(f'{client_ip}-[{current_time}] "GET", "/diaries" 404  member: {member_id}, nickname: {nickname}, snslink를 찾을 수 없습니다.')
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)


# 일기장 링크공유


# class DiaryTextBoxManager(APIView):
#
#     @swagger_auto_schema(query_serializer=DiaryTextBoxPostRequestSerializer,responses={200:DiaryTextBoxPostResponseSerializer})
#     def post(self, request):
#         diary_instance = get_object_or_404(Diary, diary_id=request.query_params.get('diary_id'))
#         content = request.query_params.get('content')
#         diarytextbox_serializer = DiaryTextBoxCreateSerializer(data={'content': content})
#
#         if diarytextbox_serializer.is_valid():
#             diarytextbox_pk = diarytextbox_serializer.save(diary=diary_instance)
#             return Response({'textbox_id': diarytextbox_pk.pk}, status=status.HTTP_201_CREATED)
#
#         else:
#             return Response(status=status.HTTP_400_BAD_REQUEST)


class DiaryStickerManager(APIView):
    @swagger_auto_schema(operation_summary="DALLE 스티커 생성",
                         operation_description="content (일기 내용)을 받아와서 s3에 업로드된 url반환",
                         request_body=DiaryStickerRequestSerializer,
                         responses={201: DiaryStickerGetResponseSerializer})
    def post(self, request, format=None):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nickname = request.session.get('nickname')
        member_id = request.session.get('member_id')
        start = time.time()
        print(request.data.get('content'))
        try:
            content = request.data.get('content')

            # DiaryTextBox 모델에 데이터 저장
            # diary_text_box = DiaryTextBox.objects.create(content=content)

            # 일기 내용에서 상위 3개 키워드 추출
            # comprehend 안들어가는 경우 예외 처리 필요****
            top_keywords = extract_top_keywords(content)
            print(top_keywords)

            if not top_keywords:
                response_data = {
                    'code': 'D001',
                    'status': '200',
                    'message': '키워드가 생성되지 않았습니다.'
                }
                return Response(response_data, status=200)

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
            logger.info(f'{client_ip}-[{current_time}] "POST", "/diaries" 201  member: {member_id}, nickname: {nickname}, 이미지 생성 성공, {uploaded_image_urls}, 생성시간:{end - start:.5f}')
            return Response(response_data, status=201)
        except NoCredentialsError:
            logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 500  member: {member_id}, nickname: {nickname}, AWS credentials not available.')
            return Response({"message": "AWS credentials not available."}, status=500)
        except Exception as e:
            response_data = {
                'code': 'D001',
                'status': '500',
                'message': f'에러 발생: {str(e)}',
            }
            logger.error(f'{client_ip}-[{current_time}] "POST", "/diaries" 500  member: {member_id}, nickname: {nickname}, {str(e)}')
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
