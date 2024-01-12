from rest_framework import serializers


class PostSignupRequestSerializer(serializers.Serializer):
    login_id = serializers.CharField()
    nickname = serializers.CharField()
    password = serializers.CharField()


class PostSignupResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()


class PostLoginRequestSerializer(serializers.Serializer):
    login_id = serializers.CharField()
    password = serializers.CharField()


class PostLoginResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()


# class PostLogoutRequestSerializer(serializers.Serializer):



class PostLogoutResponseSerializer(serializers.Serializer):
    code = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()