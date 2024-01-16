from rest_framework import serializers, viewsets
from .models import Member
from django.db import IntegrityError


class MemberSerializer(serializers.Serializer):
    login_id = serializers.CharField()
    nickname = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        login_id = validated_data.get('login_id')
        nickname = validated_data.get('nickname')
        password = validated_data.get('password')

        try:
            member = Member(login_id=login_id, nickname=nickname, password=password)
            member.save()
            return {

                "code": "M001",
                "status": 201,
                "message": "회원가입 완료"
            }
        except IntegrityError as e:
            # 중복된 login_id가 이미 존재하는 경우의 예외 처리
            return {
                "code": "M002",
                "status": 400,
                "message": "이미 존재하는 로그인 ID입니다."
            }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member

class SignSerializer(serializers.Serializer):
    login_id = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, validated_data):
        login_id = validated_data.get('login_id')
        password = validated_data.get('password')

        # 사용자 식별자(login_id)를 기반으로 사용자 찾기
        member = Member.objects.filter(login_id=login_id).first()

        if not member:
            raise serializers.ValidationError("잘못된 로그인 아이디 입력")

        # 비밀번호 직접 비교
        if password != member.password:
            raise serializers.ValidationError("잘못된 비밀번호 입력")

        # 여기서 필요한 추가 검증 로직을 수행할 수 있습니다.

        # 최종적으로 검증된 데이터 반환
        validated_data['member_id'] = member.member_id
        validated_data['nickname'] = member.nickname
        return validated_data

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = UserSerializer