from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404

from .models import Diary
from .serializers import (DiaryDetailSerializer, DiaryListSerializer, DiarySnsLinkSerializer,
                          DiaryCreateSerializer, DiaryFinalSaveSerializer)


# Create your views here.

class Diaries(APIView):
    # 일기장 조회
    @staticmethod
    def get(request, diary_id=None):
        found_diary = get_object_or_404(Diary, diary_id=diary_id)
        try:
            serialized_diary = DiaryDetailSerializer(found_diary).data
            return Response(status=status.HTTP_200_OK, data=serialized_diary)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # 일기장 생성
    @staticmethod
    def post(request):
        diary_serializer = DiaryCreateSerializer(data=request.data)

        if diary_serializer.is_valid():
            diary_instance = diary_serializer.save()
            return Response({"diary_id": diary_instance.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)

    # 일기장 최종 저장
    @staticmethod
    def put(request, diary_id):
        if diary_id is None:
            return Response({"error": "diary does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            diary_instance = get_object_or_404(Diary, id=diary_id)
        except ObjectDoesNotExist:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)
        diary_serializer = DiaryFinalSaveSerializer(diary_instance, data=request.data)

        if diary_serializer.is_valid():
            diary_serializer.save()
            return Response({"message": "Diary saved successfully"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "diary does not exist"}, status=status.HTTP_404_NOT_FOUND)


class DiaryManager(APIView):

    # 일기장 링크공유
    @staticmethod
    def get(request):
        diary_id = request.GET.get('diary_id')

        if diary_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            sns_link = DiarySnsLinkSerializer(Diary.objects.get(id=diary_id))
            return Response(status=status.HTTP_200_OK, data=sns_link.data)
        except ObjectDoesNotExist:
            return Response({"error": "diary snsLink does not exist"}, status=status.HTTP_404_NOT_FOUND)
