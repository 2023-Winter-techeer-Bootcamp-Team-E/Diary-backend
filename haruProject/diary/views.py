from calendar import Calendar
import logging
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from member.models import Member
from .models import Diary
from harucalendar.models import Harucalendar
from member.models import Member
from .serializers import (DiaryDetailSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryTextBoxCreateSerializer,
                          DiaryStickerCreateSerializer, DiaryUpdateSerializer)
from harucalendar.serializer import HarucalendarCreateSerializer
from .utils import extract_top_keywords, generate_sticker_images
from botocore.exceptions import NoCredentialsError

import time
from .tasks import upload_image_to_s3

from .swaggerserializer import DiaryGetResponseSerializer, DiaryLinkGetResponseSerializer, \
    DiaryTextBoxPutRequestSerializer, DiaryStickerRequestSerializer, \
    DiaryStickerGetResponseSerializer, SwaggerDiaryCreateRequestSerializer, SwaggerDiaryCreateResponseSerializer, \
    DiaryGetRequestSerializer, DiaryLinkRequestSerializer

from datetime import datetime



# Create your views here.

logger = logging.getLogger(__name__)
class DiariesGet(APIView):
    # 일기장 조회
    @swagger_auto_schema(
        operation_description="일기에 연동 된 텍스트박스,스티커 등등 출력<br>1.해당달에 존재 하는 전반적인 일기 목록은 캘린더 조회에서 확인<br> 2.일기의 세부 내용(스티커,텍스트박스 등) 출력",
        operation_summary="일기 조회",
        #query_serializer=DiaryGetRequestSerializer,
        responses={200: DiaryGetResponseSerializer}
    )
    def get(self, request, diary_id):
        try:
            client_ip = request.META.get('REMOTE_ADDR', None)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # day = request.GET.get('day')  # swagger에서는 GET, postman은 data
            # calendar_id = request.session.get('calendar_id')
            # found_diary = Diary.objects.get(day=day, calendar_id=calendar_id)
            # request.session['diary_id'] = found_diary.diary_id

            diary_instance = Diary.objects.get(pk=diary_id)
            calendar_id = diary_instance.calendar_id
            calendar_instance = Harucalendar.objects.get(pk=calendar_id)
            member_id = calendar_instance.member_id
            member_instance = Member.objects.get(pk=member_id)
            nickname = member_instance.nickname
            serialized_diary = DiaryDetailSerializer(diary_instance).data
            # 출력값에 nickname, day 출력, 임시코드이고 추후 깔끔하게 리펙터링 하겠음-우성-
            logger.info(f'INFO {client_ip} {current_time} GET api/v1/diaries//DiriesGet 200 diary is required')
            return Response(status=status.HTTP_200_OK, data={"diary_data":serialized_diary, "day": diary_instance.day, "nickname":nickname})
        except ObjectDoesNotExist:
            logger.warning(f'INFO {client_ip} {current_time} GET api/v1/diaries//DiriesGet 404 diary does not exist')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

class DiariesPost(APIView):
    @staticmethod
    @swagger_auto_schema(
        operation_description="일기 배경지 고르기<br>1.일기배경지 고르기<br> 2.sns링크 반환",
        operation_summary="일기초안 생성(배경지 고르기)",
        request_body=SwaggerDiaryCreateRequestSerializer,
        responses={200: SwaggerDiaryCreateResponseSerializer},
        manual_parameters=[
            openapi.Parameter('diary_id', openapi.IN_QUERY, description="Diary ID", type=openapi.TYPE_INTEGER,required=False),]
    )
    def post(request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # calendar_id,year_month,member_id만 세션으로 받고, day만 request로 받을거임
        calendar_id = request.session.get('calendar_id')
        year_month = request.session.get('year_month')
        member_id = request.session.get('member_id')
        nickname = request.session.get('member_nickname')
        day = request.data.get('day')
        diary_bg_id = request.data.get('diary_bg_id')

        if member_id is None:
            logger.warning(f'WARNING {client_ip} {current_time} POST api/v1/diaries//DiriesPost 400 Login required')
            return Response({'error': '로그인이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

        if calendar_id is None:
            member_instance = get_object_or_404(Member, member_id=member_id)
            calendar_serializer = HarucalendarCreateSerializer(data={'year_month': year_month})
            if calendar_serializer.is_valid():
                calendar_instance = calendar_serializer.save(member=member_instance)
                calendar_id = calendar_instance.calendar_id
                request.session['calendar_id'] = calendar_id  # 캘린더를 만들어주고 session에 calendar_id 최신화.

            else:
                logger.warning(f'WARNING {client_ip} {current_time} POST api/v1/diaries//DiriesPost 400 {calendar_serializer.errors}')
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '멤버와 캘린더 값이 유효하지 않습니다.'})

            diary_data = {'diary_bg_id': diary_bg_id, 'year_month': year_month, 'day': day}

            diary_serializer = DiaryCreateSerializer(data=diary_data)
            if diary_serializer.is_valid():
                member_object = Member.objects.get(member_id=member_id)
                diary_instance = diary_serializer.save(calendar=calendar_instance)
                sns_data = {"sns_link": f"http://{request.get_host()}/api/v1/harurooms/{diary_instance.diary_id}"}
                diary_update_serializer = DiaryUpdateSerializer(diary_instance, data=sns_data)
                if diary_update_serializer.is_valid():
                    diary_update_serializer.save()
                    response_data = {
                        "diary_id": diary_instance.diary_id,
                        "diary_bg_id": diary_instance.diary_bg_id,
                        "sns_link": sns_data,
                        "year_month": year_month,
                        "day": day,
                        "nickname": member_object.nickname}
                    logger.info(f'INFO {client_ip} {current_time} POST api/v1/diaries//DiriesPost 200 diary created')
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    logger.error(f'ERROR {client_ip} {current_time} POST api/v1/diaries//DiriesPost 400 {diary_serializer.errors}')
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'snsLink가 유효하지 않습니다.'})

        if calendar_id is not None:
            diary_exist = Diary.objects.filter(calendar=calendar_id, day=day).exists()

            if diary_exist:
                return Response({'error': '해당 일에 이미 일기가 있습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            diary_data = {'diary_bg_id': diary_bg_id, 'year_month': year_month, 'day': day}
            diary_serializer = DiaryCreateSerializer(data=diary_data)
            if diary_serializer.is_valid():
                diary_instance = diary_serializer.save(calendar_id=calendar_id)
                sns_data = {"sns_link": f"http://{request.get_host()}/api/v1/harurooms/{diary_instance.diary_id}"}
                diary_update_serializer = DiaryUpdateSerializer(diary_instance, data=sns_data)
                if diary_update_serializer.is_valid():
                    diary_update_serializer.save()
                    response_data = {
                        "diary_id": diary_instance.diary_id,
                        "diary_bg_id": diary_instance.diary_bg_id,
                        "year_month": year_month,
                        "day": day,
                        "nickname": nickname,
                        "sns_link": sns_data}
                    logger.info(f'INFO {client_ip} {current_time} POST api/v1/diaries//DiriesPost 200 diary created')
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    logger.error(f'ERROR {client_ip} {current_time} POST api/v1/diaries//DiriesPost 400 {diary_update_serializer.errors}')
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'snsLink가 유효하지 않습니다.'})
            else:
                logger.error(f'ERROR {client_ip} {current_time} POST api/v1/diaries//DiriesPost 400 {diary_serializer.errors}')
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '일기 생성 데이터가 유효하지 않습니다..'})


class DiariesSave(APIView):
    @swagger_auto_schema(operation_description="일기 최종 저장",
                         operation_summary="기존 만들어진 일기에 일기 텍스트 박스 및 스티커 정보 저장",
                         request_body=DiaryTextBoxPutRequestSerializer,
                         responses={200: 'DiaryTextBoxPutResponseSerializer'},
                         )
    def put(self, request):  # 캘린더 아디랑
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nickname = request.session.get('nickname')
        member_id = request.session.get('member_id')
        diary_id = request.session.get('diary_id')
        if diary_id is None:
            logger.warning(f'WARNING {client_ip} {current_time} PUT api/v1/diaries//DiariesSave 400 diary does not exist')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if request.data is None:
            logger.warning(f'WARNING {client_ip} {current_time} POST api/v1/diaries//DiariesSave 400 diary does not exist')
            return Response({"error": "diary data does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            diary_instance = get_object_or_404(Diary, diary_id=diary_id)
        except ObjectDoesNotExist:
            logger.warning(f'WARNING {client_ip} {current_time} POST api/v1/diaries//DiariesSave 400 diary does not exist')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        diary_instance.is_expiry = True
        diary_instance.save()
        textboxs_data = request.data.get('textboxs', [])
        stickers_data = request.data.get('stickers', [])
        try:
            for sticker_data in stickers_data:
                sticker_serializer = DiaryStickerCreateSerializer(data=sticker_data)
                if sticker_serializer.is_valid():
                    sticker_serializer.save(diary=diary_instance)
                else:
                    logger.error(f'ERROR {client_ip} {current_time} PUT api/v1/diaries//DiariesSave 400 {sticker_serializer.errors}')
                    Response({"error": "sticker error"}, status=status.HTTP_404_NOT_FOUND)
            for textbox_data in textboxs_data:
                textbox_serializer = DiaryTextBoxCreateSerializer(data=textbox_data)
                if textbox_serializer.is_valid():
                    textbox_serializer.save(diary=diary_instance)
                else:
                    logger.error(f'ERROR {client_ip} {current_time} PUT api/v1/diaries//DiariesSave 400 {textbox_serializer.errors}')
                    Response({"error": "textbox error"}, status=status.HTTP_404_NOT_FOUND)

            logger.info(f'INFO {client_ip} {current_time} PUT api/v1/diaries/DiariesSave 400 diary saved successfully')
            return Response({'code': 'D001', 'status': '201', 'message': '일기장 저장 성공!'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            logger.warning(f'WARNING {client_ip} {current_time} PUT api/v1/diaries//DiariesSave 404 diary does not exist')
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)


# 일기장 링크공유
class DiaryManager(APIView):
    @swagger_auto_schema(operation_summary="작성중인 일기 링크 조회",
                         operation_description="작성중인 일기의 링크 및 diary_id, day, nickname, sns_lin 반환",
                         query_serializer=DiaryLinkRequestSerializer,
                         responses={200: DiaryLinkGetResponseSerializer})
    def get(self, request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # nickname = request.session.get('nickname')
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
            logger.info(f'INFO {client_ip} {current_time} GET api/v1/diaries//DiaryManager 200 diary link required')
            return Response(response_data, status=200)
        except ObjectDoesNotExist:
            logger.warning(f'WARNING {client_ip} {current_time} GET api/v1/diaries//DiaryManager 200 diary snsLink does not exist')
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)


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
                logger.warning(f'WARNING {client_ip} {current_time} POST api/v1/diaries//DiaryStickerManager 200 keywords are not created')
                return Response(response_data, status=200)

            # 상위 키워드로 DALL-E API 호출하여 스티커 이미지 생성
            sticker_image_urls = generate_sticker_images(top_keywords)
            # 이미지 업로드 및 URL 반환
            uploaded_image_urls = []
            for keyword, sticker_url in sticker_image_urls.items():
                result = upload_image_to_s3.delay(sticker_url, keyword)
                response = result.get()
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
            logger.info(f'INFO {client_ip} {current_time} POST api/v1/diaries//DiaryStickerManager 201 images are created')
            return Response(response_data, status=201)
        except NoCredentialsError:
            logger.error(f'ERROR {client_ip} {current_time} POST api/v1/diaries//DiaryStickerManager 500 AWS credentials not available.')
            return Response({"message": "AWS credentials not available."}, status=500)
        except Exception as e:
            response_data = {
                'code': 'D001',
                'status': '500',
                'message': f'에러 발생: {str(e)}',
            }
            logger.error(f'ERROR {client_ip} {current_time} POST api/v1/diaries//DiaryStickerManager 500 {str(e)}')
            return Response(response_data, status=500)
