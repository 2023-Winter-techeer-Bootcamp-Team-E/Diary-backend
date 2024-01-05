from django.shortcuts import render

from .models import Guest
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GuestSerializer
from django.shortcuts import get_object_or_404

# 게스트 생성 뷰
class CreateGuestView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = GuestSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)


# 게스트 확인 뷰
'''
class CheckGuestPasswordView(APIView):
    def get(self, request, guests_id):
        password = request.query_params.get('password')
        guest = get_object_or_404(Guest, guest_id=guests_id)

        if str(guest.guest_pw) == password:
            return Response({
                "code": "G001",
                "status": "200",
                "message": "게스트 조회 성공"
            }, status=200)
        else:
            return Response({
                "code": "G002",
                "status": "401",
                "message": "잘못된 비밀번호"
            }, status=401)
'''