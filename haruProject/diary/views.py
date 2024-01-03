from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Diary
from .serializers import (DiaryDetailSerializer, DiaryListSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryFinalSaveSerializer)


# Create your views here.

class Diaries(APIView):
    # 일기장 조회
    @staticmethod
    def get(request):
        diary_id = request.GET.get('diary_id')
        if diary_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            found_diary = DiaryDetailSerializer(Diary.objects.get(id=diary_id))
            return Response(status=status.HTTP_200_OK, data=found_diary.data)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # 일기장 최종 저장
    @staticmethod
    def post(request):
        diary_id = request.GET.pop('diary_id')
        if diary_id is None:
            return Response({"error : diary does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        diary_serializer = DiaryFinalSaveSerializer(diary_id, data=request.data)

        if diary_serializer.is_valid():
            diary_serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response({"error" : "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DiaryManager(APIView):

    # 일기장 링크공유
    def get(self, request):
        pass

    # 일기장 생성
    def post(self, request):
        pass
