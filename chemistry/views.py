from django.shortcuts import render
from rest_framework.views import APIView
from ocr import mathpix
from .wolfram import *
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
class ChemistryView(APIView):
    def post(self,request):
        # get data
        # validate subscription
        # pass query to wolfram
        query=mathpix.run_ocr(request.data['image'])
        if request.data['mode']=='Balance':     
            result='this feature is coming soon'
            response_data={
            'question':[                {'type':'latex','format':'tex','data':query}
            ],
            'answer':[
            {'type':'text','format':'txt','data':result},
            ]
            }
            return Response(response_data,status=status.HTTP_200_OK)
        elif request.data['mode']=='Auto':
            answer=auto_solve(query,'plaintext')
            response_data={
            'quesion':[
                {'type':'latex','format':'tex','data':query}
            ],
            'answer':[
            {'type':'text','format':'txt','data':answer}
            ]
            }
            return Response(response_data,status=status.HTTP_200_OK)
        else:
            print('server error')
            return Response({'message':'Server error'},status=status.HTTP_401_UNAUTHORIZED)    
         