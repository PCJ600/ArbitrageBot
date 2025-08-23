from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.


class TestView(APIView):
    def post(self, request, *args, **kwargs):

        return Response(status=status.HTTP_200_OK)

