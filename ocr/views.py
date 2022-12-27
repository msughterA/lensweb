from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ocr import mathpix


# Create your views here.
class OCRView(APIView):
    def post(self, request):
        # run the ocr and return rext
        data_status, text = mathpix.get_text(request.data["image"])
        response_data = {"text": text}
        if data_status:
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {"message": "Server error"}
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
