from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Harucalendar
from .serializer import HarucalendarAllSerializer, HarucalendarstickerAllSerializer, \
    HarucalendarStickerCreateSerializer, HarucalendarCreateSerializer
from rest_framework.views import APIView
from diary.models import Diary

from .swaggerserializer import HarucalendarstickerRequestSerializer, HarucalendarstickerGetResponseSerializer, \
    HarucalendarRequestSerializer, HarucalendarGetResponseSerializer


class HarucalendarView(APIView):  # 캘린더 조회

    @swagger_auto_schema(query_serializer=HarucalendarRequestSerializer,
                         responses={200: HarucalendarGetResponseSerializer})
    def get(self, request):
        try:
            member_id = request.query_params.get('member_id')
            year_month_day = request.query_params.get('year_month_day') #뉴진스랑 상의
            harucalendar = get_object_or_404(Harucalendar, member=member_id, year_month_day=year_month_day)
            # 조회가 성공하면 쿠키에 켈린더아이디랑 멤버아이디 기입, 기존 멤버아이디가 있는 쿠키에 캘린더 아이디를 심어 쓰기 선택.
            #만든걸 리스폰스에 같이 심어서 보내주기.
        except ObjectDoesNotExist:
            return Response({'message': '달력이 존재하지 않습니다.'},
                            status=status.HTTP_404_NOT_FOUND)

        diary = Diary.objects.filter(calendar=harucalendar.calendar_id)
        diary_list = []

        for item in diary:  # 하루다이어리에서 다이어리id, 만료여부를 리스트에 저장
            diary_list.append({
                'diary_id': item.diary_id,
                'is_expiry': item.is_expiry,
                'diary_day': item.diary_day
            })


        # calendar_session_list = []
        # for item in Diary.objects.all():
        #     diary_textboxes = item.diaryTextBoxs.all()
        #
        #     calendar_session_list.append({
        #         'diary_date': item.diary_date,  # DiaryTextBox 모델의 diary_date 가져오기
        #         'is_expird': item.is_expiry,
        #         'day': item.diary_day,
        #         'diary_textboxes': [{'writer': textbox.writer, 'content': textbox.content} for textbox in
        #                             diary_textboxes]
        #     })

        # request.session['calendar_session_list'] = calendar_session_list

        harucalendarserializer = HarucalendarAllSerializer(harucalendar)  # 캘린더 시리얼라이징

        request.session['calendar_id'] = harucalendarserializer.data['calendar_id']

        # session checking
        # for key, value in request.session.items():
        #     print(f'세션 키: {key}, 세션 값: {value}')

        return Response({
            'code': 'C001',
            'status': '200',
            'message': '달력 조회 성공',
            'data': harucalendarserializer.data,
            'diaries': diary_list,
        }, status=status.HTTP_200_OK)


class HarucalendarstickerView(APIView):
    @swagger_auto_schema(query_serializer=HarucalendarstickerRequestSerializer,
                         responses={200: HarucalendarstickerGetResponseSerializer})
    def post(self, request):
        try:
            stickers_data = request.data.get('stickers', [])
            for sticker_data in stickers_data:
                calendar_id = sticker_data.get('calendar_id')
                sticker_url = sticker_data.get('sticker_image_url')
                if calendar_id is None:
                    return Response({'error': 'stickers 내부의 calendar_id가 제공되지 않았습니다.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif sticker_url is None:
                    return Response({'error': '스티커 URL이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    harucalendar_instance = get_object_or_404(Harucalendar, calendar_id=calendar_id)
                    sticker_serializer = HarucalendarStickerCreateSerializer(data=sticker_data)
                    if sticker_serializer.is_valid():
                        sticker_serializer.save(calendar=harucalendar_instance)
                    else:
                        print(sticker_serializer.errors)
                        return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response({'code': 'c002', 'status': '200', 'message': '스티커 추가 성공'}, status=200)

        except ObjectDoesNotExist:
            return Response({'error': '켈린더가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


'''
class serializertest(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(query_serializer=IncrementedValueSerializer,responses={"200":GetResponseSerializer})
    def get(self, request):
        result = request.get.get('value')
        result = result + 10
        return Response({'data': result}, status=status.HTTP_200_OK)
'''
