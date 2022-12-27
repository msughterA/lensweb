from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import FileReceive, FileSend


# Create your views here.
class FileReceiveView(APIView):
    def post(self, request):
        pass


class FileSendView(APIView):
    def post(self, request):
        pass
