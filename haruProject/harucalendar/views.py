from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework import status
from .models import Harucalendar
from .serializer import HarucalendarAllSerializer, HarucalendarstickerAllSerializer
from rest_framework.views import APIView
from ..diary.models import Diary


class HarucalendarView(APIView):  # 캘린더 조회
    def get(self, request, member_id):
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))

            harucalendar = Harucalendar.objects.get(pk=member_id,
                                                    year_month__year=year,
                                                    year_month__month=month,
                                                    )  # lockup을 통해 켈린더의 연과 월만 조회
        # 순서가 다이어리 -> 달력으로 가므로 , 어차피 다이어리는 연-월 로 인덱싱이 되있으므로, 굳이 아래 로직에서 연-월로 필터링 할 필요가 없음.

        except ObjectDoesNotExist:
            return Response({'message': '달력이 존재하지 않습니다.'},
                            status=status.HTTP_404_NOT_FOUND)

        diary=Diary.objects.filter(calendar_id=harucalendar.calendar_id)
        diary_list = []

        for item in diary:  # 하루다이어리에서 다이어리id, 만료여부를 리스트에 저장
            diary_list.append({
                'diary_id': item.diary_id,
                'is_expired': item.is_expired
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
    def post(self, request):
        try:
            exist_or_not = Harucalendar.objects.get(pk=request.calendar_id)

        except ObjectDoesNotExist:
            return Response({'error': '켈린더가 없습니다.'})

        # 프론트에서 열심히 붙힌 스티커 DB 저장
        sticker_data = request.data.get('stikers', [])  # request data를 리스트 형식으로 정렬

        for sticker_data_ in sticker_data:
            if 'sticker_image_url' not in sticker_data_:
                return Response({'error': '스티커 url이 없습니다 !'})

            serializer = HarucalendarstickerAllSerializer(data=sticker_data_)

            if serializer.is_valid():
                serializer.save(calendar_id=request.calendar_id)

            else:
                return Response({'error': 'serializer.errors'}, status=400)
