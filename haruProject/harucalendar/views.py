from rest_framework.generics import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from .models import Harucalendar
from .serializer import HarucalendarAllSerializer, HarucalendarstickerAllSerializer
from rest_framework.views import APIView
from diary.models import Diary


class HarucalendarView(APIView):  # 캘린더 조회
    @staticmethod
    def get(request, member_id):
        try:

            year = request.GET.get('year')
            month = request.GET.get('month')
            day = request.GET.get('day')
            year_month_day = f'{year}{month}{day}'
            harucalendar = get_object_or_404(Harucalendar, member_id=member_id, year_month_day=year_month_day)

        except ObjectDoesNotExist:
            return Response({'message': '달력이 존재하지 않습니다.'},
                            status=status.HTTP_404_NOT_FOUND)

        diary = Diary.objects.filter(calendar_id=harucalendar.calendar_id)
        diary_list = []

        for item in diary:  # 하루다이어리에서 다이어리id, 만료여부를 리스트에 저장
            diary_list.append({
                'diary_id': item.diary_id,
                'is_expiry': item.is_expiry
                # 추후 day 출력하는 로직 추가 예정
            })

        harucalendarserializer = HarucalendarAllSerializer(harucalendar)  # 캘린더 시리얼라이징

        return Response({
            'code': 'C001',
            'status': '200',
            'message': '달력 조회 성공',
            'data': harucalendarserializer.data,
            'diaries': diary_list,
        }, status=status.HTTP_200_OK)


class HarucalendarstickerView(APIView):  # 스티커 부착
    @staticmethod
    def post(request):
        try:
            # exist_or_not = get_object_or_404(Harucalendar, calendar_id=request.data.calendarid)
            calendar_id = request.query_params.get('calendarid')
            exist_or_not = get_object_or_404(Harucalendar, calendar_id=calendar_id)
        except ObjectDoesNotExist:
            return Response({'error': '켈린더가 없습니다.'})

        # 프론트에서 열심히 붙힌 스티커 DB 저장
        sticker_data = request.data.get('stikers', [])  # request data를 리스트 형식으로 정렬

        for sticker_data_ in sticker_data:
            if 'sticker_image_url' not in sticker_data_:
                return Response({'error': '스티커 url이 없습니다 !'})

            serializer = HarucalendarstickerAllSerializer(data=sticker_data_)

            if serializer.is_valid():
                serializer.save(calendar_id=calendar_id)

            else:
                return Response({'error': 'serializer.errors'}, status=400)

        return Response({'code': 'c002', 'status': '200', 'message': '스티커 추가 성공'}, status=200)
