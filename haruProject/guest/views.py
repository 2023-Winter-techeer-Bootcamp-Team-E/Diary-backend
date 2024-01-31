from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Guest
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GuestCreateSerializer


# 게스트 생성 뷰
class GuestCreateView(APIView):
    @swagger_auto_schema(
        request_body=GuestCreateSerializer,
        responses={
            201: openapi.Response("게스트가 성공적으로 생성되었습니다.", GuestCreateSerializer),
            400: "잘못된 요청",
        },
        operation_description="새로운 게스트 생성",
    )
    def post(self, request, *args, **kwargs):

        guest_pw = request.data.get('guest_pw')
        diary_id = kwargs.get('diary_id')  # URL 패턴에서 diary_id를 가져오기

        guest_data = {'guest_pw': guest_pw, 'diary': diary_id}
        serializer = GuestCreateSerializer(data=guest_data)
        if serializer.is_valid():
            guest = serializer.save()
            request.session['guest_id'] = guest.guest_id

            response_data = {
            "data": {"guest_id": guest.guest_id},
            "code": "G001",
            "status": 201,
            "message": "게스트 생성 성공"
        }
            # 생성된 게스트에 접근하여 추가적인 작업 수행 가능
            return Response({"guest_id": guest.guest_id}, status=201)
        else:
            return Response(serializer.errors, status=400)
