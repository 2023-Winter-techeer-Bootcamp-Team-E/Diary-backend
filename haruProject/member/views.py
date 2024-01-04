from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MemberSerializer, SignSerializer


class SignUpView(APIView):
    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=201)
        return Response(serializer.errors, status=400)


class LogInView(APIView):
    def post(self, request):
        serializer = SignSerializer(data=request.data)
        if serializer.is_valid():
            # serializer에서 유효성 검사를 통과한 경우
            login_id = serializer.validated_data['login_id']

            # 로그인 성공
            request.session['login_id'] = login_id
            return Response(
                {
                    "code": "A001",
                    "status": 200,
                    "message": "로그인 성공",
                },
                status=status.HTTP_200_OK)
        else:
            # serializer에서 유효성 검사를 통과하지 못한 경우
            return Response(
                {
                    "code": "A001_2",
                    "status": "401",
                    "message": "로그인 실패",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST)


class LogOutView(APIView):
    def post(self, request):

        request.session.flush()
        return Response(
            {
                "code": "A002",
                "status": "200",
                "message": "로그아웃 성공",
            },
            status=status.HTTP_200_OK)
