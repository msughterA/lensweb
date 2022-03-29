from django.shortcuts import render
import openai
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from ocr import mathpix
import os
from . import wolfram


# Create your views here.


# Put the prompt in the proper format
def format_prompt(prompt):
    new_prompt=f"I am a highly intelligent question answering bot. If you ask me a question that is rooted in truth, I will give you the answer. If you ask me a question that is nonsense, trickery, or has no clear answer, I will respond with \"Unknown\".\n\nQ: What is human life expectancy in the United States?\nA: Human life expectancy in the United States is 78 years.\n\nQ: Who was president of the United States in 1955?\nA: Dwight D. Eisenhower was president of the United States in 1955.\n\nQ: Which party did he belong to?\nA: He belonged to the Republican Party.\n\nQ: What is the square root of banana?\nA: Unknown\n\nQ: How does a telescope work?\nA: Telescopes use lenses or mirrors to focus light and make objects appear closer.\n\nQ: Where were the 1992 Olympics held?\nA: The 1992 Olympics were held in Barcelona, Spain.\n\nQ: How many squigs are in a bonk?\nA: Unknown\n\nQ: {prompt}?\nA:"
    return new_prompt

def get_answer(prompt):
    prompt=format_prompt(prompt)
    return openai.Completion.create(
                                    engine="text-davinci-002",
                                    prompt=prompt,
                                    temperature=0,
                                    max_tokens=100,
                                    top_p=1,
                                    frequency_penalty=0.0,
                                    presence_penalty=0.0,
                                    stop=["\n"]
                                    )['choices'][0]['text']
    
    
class GstView(APIView):
    def post(self,request):
        try:
            query,ascii_text=mathpix.run_ocr(request.data['image'])
        except:
            return Response({'message':'Server error'},status=status.HTTP_400_BAD_REQUEST)    
        # check for subscription validity
        if request.data['mode']=='Theory':
            is_wolfram_answered,wa=wolfram.wolfram_answer(query,'plaintext')
            if is_wolfram_answered==True:
                answer=wa
            else:    
                answer=get_answer(query)
            #print(answer)
            response_data={
                'question':[
                    {'type':'latex','format':'tex','data':query}
                ],
                'answer':[
                    {'type':'latex','format':'tex','data':answer}
                ]
            } 
            return Response(response_data,status=status.HTTP_200_OK)  
        elif request.data['mode']=='Objective':
            return Response({'message':'This Feature is not yet available try using the Theory mode to answer the question'},status=status.HTTP_401_UNAUTHORIZED)
        
