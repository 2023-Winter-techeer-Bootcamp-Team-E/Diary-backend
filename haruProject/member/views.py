from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import MemberSerializer, SignSerializer
from .swagger_serializers import *
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SignUpView(APIView):
    @swagger_auto_schema(
        request_body=PostSignupRequestSerializer,
        responses={"201": PostSignupResponseSerializer}
    )
    def post(self, request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            if response_data == {
                "code": "M001",
                "status": 201,
                "message": "회원가입 완료"
            }:
                logger.info(f'INFO {client_ip} {current_time} POST /members 201 signup success')
                return Response(response_data, status=201)
            else:
                logger.warning(f'WARNING {client_ip} {current_time} POST /members 400 already existing')
                return Response(response_data, status=400)
        logger.warning(f'WARNING {client_ip} {current_time} POST /members 400 signup failed')
        return Response(serializer.errors, status=400)


class LogInView(APIView):
    @swagger_auto_schema(
        request_body=PostLoginRequestSerializer,
        responses={"200": PostLoginResponseSerializer}
    )
    def post(self, request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        serializer = SignSerializer(data=request.data)
        if serializer.is_valid():
            # serializer에서 유효성 검사를 통과한 경우

            member_id = serializer.validated_data['member_id']
            nickname = serializer.validated_data['nickname']

            # 로그인 성공
            request.session['member_id'] = member_id
            request.session['nickname'] = nickname

            response_data = {
                "code": "A001",
                "status": 200,
                "message": "로그인 성공",
                "nickname": nickname
            }
            response_status = status.HTTP_200_OK
            logger.info(f'INFO {client_ip} {current_time} POST /members 200 login success ')
        else:
            # serializer에서 유효성 검사를 통과하지 못한 경우
            error_message = None
            non_field_errors = serializer.errors.get('non_field_errors', None)
            if non_field_errors:
                error_message = non_field_errors[0]

            response_data = {
                "code": "A001_2",
                "status": "401",
                "message": "로그인 실패",
                "data": error_message
            }
            response_status = status.HTTP_400_BAD_REQUEST
            logger.warning(f'WARNING {client_ip} {current_time} POST /members 200 login failed ')
        response = Response(response_data, status=response_status)
        return response


class LogOutView(APIView):
    @swagger_auto_schema(
        responses={"200": PostLogoutResponseSerializer}
    )
    def post(self, request):
        client_ip = request.META.get('REMOTE_ADDR', None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        request.session.flush()
        logger.info(f'INFO {client_ip} {current_time} POST /members 200 logout success ')
        return Response(
            {
                "code": "A002",
                "status": "200",
                "message": "로그아웃 성공",
            },
            status=status.HTTP_200_OK)
