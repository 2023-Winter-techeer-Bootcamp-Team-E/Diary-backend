from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Harucalendar, Harucalendarsticker
from .serializer import HarucalendarAllSerializer, HarucalendarstickerAllSerializer, \
    HarucalendarStickerCreateSerializer, HarucalendarCreateSerializer
from rest_framework.views import APIView
from diary.models import Diary
from member.models import Member

from .swaggerserializer import HarucalendarstickerRequestSerializer, HarucalendarstickerGetResponseSerializer, \
    HarucalendarRequestSerializer, HarucalendarGetResponseSerializer, HarucalendarstickerSerializer


class HarucalendarView(APIView):  # 캘린더 조회

    @swagger_auto_schema(
        operation_description="1.켈린더 조회 시 해당하는 캘린더가 없으면 없다고 반환(생성은X).<br>2.해당하는 캘린더가 있을 시, 해당하는 달에 있는 다이어리를 보여줌(작성유무,"
                              "다이어리id)<br>3.다이어리의 상세한 내용은 다이어리 "
                              "<br>캘린더 조회 시 세션에 calendar_id, year_month 저장",
        operation_summary="켈린더 조회",
        query_serializer=HarucalendarRequestSerializer,
        responses={200: HarucalendarGetResponseSerializer})
    def get(self, request):
        try:
            year_month = request.GET.get('year_month')  # postman에서는 data, swagger는 GET
            member_id = request.session['member_id']
            request.session['year_month'] = year_month
            harucalendar_instance = Harucalendar.objects.get(member=member_id, year_month=year_month)
            request.session['calendar_id'] = harucalendar_instance.calendar_id

        except ObjectDoesNotExist:
            request.session['calendar_id'] = None
            return Response({'message': '달력이 존재하지 않습니다.'},
                            status=status.HTTP_404_NOT_FOUND)

        diary = Diary.objects.filter(calendar=harucalendar_instance.calendar_id)
        calendar_stickers = Harucalendarsticker.objects.filter(calendar=harucalendar_instance.calendar_id)
        diary_list = []
        calendar_sticker_list = []
        for items in calendar_stickers:
            calendar_sticker_list.append({
                'sticker_image_url': items.sticker_image_url,
                'xcoor': items.xcoor,
                'ycoor': items.ycoor,
                'width': items.width,
                'height': items.height,
                'rotate': items.rotate
            })

        for items in diary:
            diary_list.append({
                'diary_id': items.diary_id,
                'is_expiry': items.is_expiry,
                'day': items.day,
                'created_at': items.created_at
            })

        harucalendarserializer = HarucalendarAllSerializer(harucalendar_instance)  # 캘린더 시리얼라이징
        request.session['calendar_id'] = harucalendarserializer.data['calendar_id']

        return Response({
            'data': harucalendarserializer.data,
            'sticker_image_url': calendar_sticker_list,
            'diaries': diary_list,
        }, status=status.HTTP_200_OK)


class HarucalendarstickerView(APIView):
    @swagger_auto_schema(
        operation_description="1.캘린더가 있는상태에서는 스티커를 바로 붙힘. <br>2.캘린더가 없으면 생성 후 스티커를 붙힘.<br>3.session으로 member_id,year_month,calendar_id 받아옴 ",
        operation_summary="캘린더 스티커 부착(캘린더 꾸미기)",
        request_body=HarucalendarstickerRequestSerializer,
        responses={200: HarucalendarstickerGetResponseSerializer})
    def post(self, request):
        new_calendar_id = None  # 초기화 추가

        try:
            member_id = request.session.get('member_id')
            calendar_id = request.session.get('calendar_id')
            year_month = request.session.get('year_month')
            stickers_data = request.data.get('stickers', [])
            print(calendar_id)
            for sticker_data in stickers_data:
                print("tq")
                if calendar_id is None:
                    member_instance = get_object_or_404(Member, member_id=member_id)
                    calendar_serializer = HarucalendarCreateSerializer(data={"year_month": year_month})
                    if calendar_serializer.is_valid():
                        new_calendar_instance = calendar_serializer.save(member=member_instance)
                        new_calendar_id = new_calendar_instance.calendar_id
                        sticker_serializer = HarucalendarStickerCreateSerializer(data=sticker_data)
                        if sticker_serializer.is_valid():
                            sticker_serializer.save(calendar=new_calendar_instance)
                        else:
                            print(sticker_serializer.errors)

                    else:
                        print(calendar_serializer.errors)
                        return Response(status=status.HTTP_400_BAD_REQUEST)

                else:
                    harucalendar_instance = get_object_or_404(Harucalendar, calendar_id=calendar_id)

                    sticker_serializer = HarucalendarStickerCreateSerializer(data=sticker_data)
                    if sticker_serializer.is_valid():
                        sticker_serializer.save(calendar=harucalendar_instance)
                    else:
                        print(sticker_serializer.errors)
                        return Response(status=status.HTTP_400_BAD_REQUEST)

        except ObjectDoesNotExist:
            return Response({'error': '켈린더가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

        if calendar_id is None:
            print(calendar_id, new_calendar_id)
            return Response(
                {'calendar_id': new_calendar_id, 'year_month': year_month, 'code': 'c002', 'status': '200',
                 'message': '스티커 추가 성공'}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'calendar_id': calendar_id, 'year_month': year_month, 'code': 'c002', 'status': '200',
                 'message': '스티커 추가 성공'}, status=status.HTTP_200_OK)

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
    # session checking
    # for key, value in request.session.items():
    #     print(f'세션 키: {key}, 세션 값: {value}')
