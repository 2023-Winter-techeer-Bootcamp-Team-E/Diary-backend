from rest_framework.generics import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from .models import Harucalendar
from .serializer import HarucalendarAllSerializer, HarucalendarstickerAllSerializer, \
    HarucalendarStickerCreateSerializer, HarucalendarCreateSerializer
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
                'is_expiry': item.is_expiry,
                'diary_day': item.diary_day
            })

        harucalendarserializer = HarucalendarAllSerializer(harucalendar)  # 캘린더 시리얼라이징

        return Response({
            'code': 'C001',
            'status': '200',
            'message': '달력 조회 성공',
            'data': harucalendarserializer.data,
            'diaries': diary_list,
        }, status=status.HTTP_200_OK)


class HarucalendarstickerView(APIView):
    @staticmethod
    def post(request):
        try:
            stickers_data = request.data.get('stickers', [])
            for sticker_data in stickers_data:
                calendar_id = sticker_data.get('calendar_id')
                sticker_url= sticker_data.get('sticker_image_url')
                if calendar_id is None:
                    return Response({'error': 'stickers 내부의 calendar_id가 제공되지 않았습니다.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif sticker_url is None:
                    return Response({'error': '스티커 URL이 없습니다.'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    harucalendar_instance = get_object_or_404(Harucalendar, calendar_id=calendar_id)
                    sticker_serializer = HarucalendarStickerCreateSerializer(data=sticker_data)
                    if sticker_serializer.is_valid():
                        sticker_serializer.save(calendar_id=harucalendar_instance)
                    else:
                        print(sticker_serializer.errors)
                        return Response({'error': '때려쳐 시발'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'code': 'c002', 'status': '200', 'message': '스티커 추가 성공'}, status=200)

        except ObjectDoesNotExist:
            return Response({'error': '켈린더가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)


