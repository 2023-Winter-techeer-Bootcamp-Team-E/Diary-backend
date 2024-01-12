from drf_yasg.utils import swagger_auto_schema

from .serializer import StaticImageSerializer
from rest_framework.views import APIView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework import status
from .models import StaticImage
from .swaggerserializer import StaticImageRequestSerializer, StaticImageGetResponseSerializer


class StaticImageView(APIView):
    @staticmethod
    @swagger_auto_schema(query_serializer=StaticImageRequestSerializer,
                         responses={200: StaticImageGetResponseSerializer})
    def get(request):
        try:
            size = request.GET.get('size', 6)  # Default size : 6, 한 페이지 당 6개의 스티커 이미지
            page_number = request.GET.get('page', 1)

            paginator = Paginator(StaticImage.objects.all(), size)

            try:
                page_objects = paginator.page(page_number)
            except PageNotAnInteger:
                page_objects = paginator.page(1)
            except EmptyPage:
                return Response({'error': 'No more pages'}, status=400)

            serialized_objects = StaticImageSerializer(page_objects, many=True).data

            st_image_urls = [obj['st_image_url'] for obj in serialized_objects]

            response_data = {
                'data': {
                    'st_image_urls': st_image_urls,
                }
            }

            return Response(response_data, status=200)

        except Exception as e:
            return Response({'error': str(e)}, status=500)
