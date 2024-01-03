from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .models import Harucalendar, Harucalendarsticker
from .serializer import HarucalendarSerializer, HarucalendarstickerSerializer
from rest_framework.views import APIView
from django.utils import timezone


class HarucalendarView(APIView):  # 캘린더 조회
    def get(self, request, member_id):
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))

            harucalendar = Harucalendar.objects.get(pk=member_id,
                                                    year_month=f'{year}{month}')  # 켈린더 안에 pk는 달력 아이디인데 member_id가 들어가도 되는가 ..?


        except ObjectDoesNotExist:
            return Response({'message': '달력이 존재하지 않습니다.'},
                            status=status.HTTP_404_NOT_FOUND)  # -> 달력을 만들어줘야하나 ? 그럼 연월등 정보는 ?

        harudies = Harudies.objects.get(calendar_id=harucalendar.calendar_id)  # 하루다이어리를 db에서 가지고옴
        diaries_list = []

        for item in harudies:  # 하루다이어리에서 다이어리id, 만료여부를 리스트에 저장
            diaries_list.append({
                'diary_id': item.diary_id,
                'is_expired': item.is_expired
            })

        harucalendarserializer = HarucalendarSerializer(harucalendar)  # 캘린더 시리얼라이징

        return Response({
            'code': 'C001',
            'status': '200',
            'message': '달력 조회 성공',
            'data': harucalendarserializer.data,
            'diaries': diaries_list,
        }, status=status.HTTP_200_OK)


class HarucalendarstickerView(APIView):  # 스티커 부착
    def post(self, request):
        try:
            exist_or_not = Harucalendar.objects.get(pk=request.calendar_id)

        except ObjectDoesNotExist:  # 캘린더가 존재하지 않을떄
            create_object = Harucalendar()

            create_object.calendar_id = request.calendar_id  # 켈린더 아이디는 유저가 ?, 아니면 자동으로 ?
            create_object.created_at = timezone.now()
            create_object.updated_at = timezone.now()
            create_object.year_month = timezone.now()  # 어떤 연월이 ??.. -> request에서 입력을 받아야 하나 ..?
            return Response({'message': '켈린더 생성완료 다시 시도해주십시오.'})

        # 프론트에서 열심히 붙힌 스티커 DB 저장
        sticker_data = request.data.get('stikers', [])  # request data를 리스트 형식으로 정렬

        for sticker_data_ in sticker_data:
            if 'sticker_image_url' not in sticker_data_:
                return Response({'error': '스티커 url이 없습니다 !'})

            serializer = HarucalendarstickerSerializer(data=sticker_data_)

            if serializer.is_valid:
                serializer.save(calendar_id=request.calendar_id)

            else:
                return Response({'error': 'serializer.errors'}, status=400)
