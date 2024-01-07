from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import ValidationError

from member.models import Member
from member.serializers import MemberSerializer
from .models import Diary
from .serializers import (DiaryDetailSerializer, DiaryListSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryTextBoxCreateSerializer,
                          DiaryStickerCreateSerializer, DiaryTextBoxSerializer)
from harucalendar.models import Harucalendar
from harucalendar.serializer import HarucalendarCreateSerializer


# Create your views here.

class Diaries(APIView):
    # 일기장 조회
    @staticmethod
    def get(request, diary_id):
        found_diary = get_object_or_404(Diary, diary_id=diary_id)
        try:
            serialized_diary = DiaryDetailSerializer(found_diary).data
            return Response(status=status.HTTP_200_OK, data=serialized_diary)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # 일기장 생성
    @staticmethod
    def post(request):
        calendar_id = request.data.get('calendar_id')
        member_id = request.data.get('member_id')

        # 날짜에서 연월만 추출
        year_month_day = request.data.get('diary_date')

        # 캘린더가 없을때
        print(calendar_id, member_id, year_month_day)
        if calendar_id is None:
            member_instance = get_object_or_404(Member, member_id=member_id)  # 멤버 인스턴스 받아오기
            calendar_serializer = HarucalendarCreateSerializer(data={'year_month_day': year_month_day})  # 캘린더 생성
            if calendar_serializer.is_valid():
                calendar_serializer.save(member_id=member_instance)  # 캘린더 생성 완료
                # 캘린더 생성 후 일기장 저장.
                new_calendar_pk = calendar_serializer.instance.pk
                new_calendar_instance = get_object_or_404(Harucalendar, calendar_id=new_calendar_pk)
                diary_serializer = DiaryCreateSerializer(data=request.data)
                if diary_serializer.is_valid():
                    diary_serializer.save(calendar_id=new_calendar_instance)
                    return Response(diary_serializer.data, status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)


            else:
                print(calendar_serializer.errors)
                return Response({'errors': '데이터 값이 유효하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)


        #캘린더가 있을떄(diary_id가 있을떄)
        else:
            calendar_instance=get_object_or_404(Harucalendar, calendar_id = request.data.get('calendar_id'))
            calendar_duplication = Harucalendar.objects.filter(year_month_day=request.data.get('diary_date'))
            if calendar_duplication:
                return Response({'error':'해당일에 이미 일기가 있습니다.'},status=status.HTTP_400_BAD_REQUEST)
            diary_serializer=DiaryCreateSerializer(data=request.data)
            if diary_serializer.is_valid():
                diary_serializer.save(calendar_id=calendar_instance)
                return Response(status=status.HTTP_200_OK)
            else:
                print(diary_serializer.errors)
                return Response(diary_serializer.data, status=status.HTTP_400_BAD_REQUEST)


    # 일기장 최종 저장
    @staticmethod
    def put(request, diary_id):
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
            return Response(status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response(status=status.HTTP_200_OK)


class DiaryManager(APIView):

    # 일기장 링크공유
    @staticmethod
    def get(request, diary_id):
        found_diary = get_object_or_404(Diary, diary_id=diary_id)

        try:
            sns_link = DiarySnsLinkSerializer(found_diary)
            return Response(status=status.HTTP_200_OK, data=sns_link.data)
        except ObjectDoesNotExist:
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)
