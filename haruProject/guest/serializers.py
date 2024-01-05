from rest_framework import serializers
from .models import Guest


class GuestSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, max_length=4)

    def validate_password(self, value):
        if not value.isdigit() or len(value) != 4:
            raise serializers.ValidationError("비밀번호는 4자리 숫자여야 합니다.")
        return value

    def create(self, validated_data):
        password = validated_data.get('password')
        guest = Guest(guest_pw=password)
        guest.save()
        return {
            "data": {
                "guest_id": str(guest.guest_id),
            },
            "code": "G001",
            "message": "게스트 생성 성공"
        }
