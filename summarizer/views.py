from django.shortcuts import render
import openai
from .models import Summarizer
from .serializers import SummarizerSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ocr import mathpix
import os
# Create your views here.

# Put the prompt in the proper format
def format_prompt(prompt):
  prompt=prompt+'tldr;'
  return prompt

openai.api_key=os.environ['OPEN_AI_KEY']
#openai.api_key=''
# openai response method
def get_response(prompt,end_of_text):
       
        prompt=format_prompt(prompt)
        return openai.Completion.create(
          engine="text-davinci-001",
          prompt=prompt,
          temperature=0.7,
          max_tokens=200,
          top_p=1.0,
          frequency_penalty=0.0,
          presence_penalty=0.0,
          stop=[end_of_text]
        )['choices'][0]
        
        
        
class SummarizerView(APIView):
  def get(self,request):
    summarizer_data=Summarizer.objects.all()
    serializer=SummarizerSerializer(summarizer_data,many=True)
    #serializer.is_valid(raise_exception=True)
    return Response(serializer.data)
  
  def post(self,request):
    query,acii_text=mathpix.run_ocr(request.data['image'])
    text=query
    # Check for subscription validity
    # Get the summary
    summary=get_response(text,'.')
    # Save the summary to database
    serializer=SummarizerSerializer(data={
      'text':text,
      'summary':summary['text']
    })
    #if serializer.is_valid(raise_exception=True):
        #serializer.save()
    response_data={
      'summary':[
       {'type':'latex','format':'tex','data':summary['text']}
      ]
      }
    return Response(response_data,status=status.HTTP_200_OK)
    #return Response({'error':'Bad Request'},status=status.HTTP_400_BAD_REQUEST) 
        