from django.shortcuts import render
from rest_framework.views import APIView
from mathematics.wolfram import auto_solve, prove_equations, simplify_expression, solve_equations
from ocr import mathpix
from .wolfram import simplify_expression,solve_equations,auto_solve
from rest_framework import status
from rest_framework.response import Response

# Create your views here.
class MathView(APIView):
    def post(self,request):
        # get data
        # validate subscription
        # pass query to wolfram
        query=mathpix.run_ocr(request.data['image'])
        if request.data['mode']=='Solve':     
            result,steps=solve_equations(query)
            response_data={
            'question':[
                {'type':'latex','format':'tex','data':query}
            ],
            'answer':[
            {'type':'text','format':'txt','data':result},
            {'type':'latex','format':'tex','data':steps}
            ]
            }
            return Response(response_data,status=status.HTTP_200_OK)
            
        elif request.data['mode']=='Simplify':
            result,steps=simplify_expression(query)
            response_data={
            'question':[
                {'type':'latex','format':'tex','data':query}
            ],
            'answer':[
            {'type':'text','format':'txt','data':result},
            {'type':'latex','format':'tex','data':steps}
            ]
            } 
            return Response(response_data,status=status.HTTP_200_OK) 
            #return response
        elif request.data['mode']=='Prove':
            result,steps=prove_equations(query)
            response_data={
            'quesion':[
                {'type':'latex','format':'tex','data':query}
            ],
            'answer':[
            {'type':'text','format':'txt','data':result},
            {'type':'latex','format':'tex','data':steps}
            ]
            }
            return Response(response_data,status=status.HTTP_200_OK)
        elif request.data['mode']=='Auto':
            answer=auto_solve(query,'mathml')
            print(f'THIS IS THE ANSWER {answer}')
            response_data={
            'question':[
                {'type':'latex','format':'tex','data':query}
            ],
            'answer':answer
            }
            return Response(response_data,status=status.HTTP_200_OK)
        else:
            print('server error')
            return Response({'message':'Server error'},status=status.HTTP_401_UNAUTHORIZED)    
         