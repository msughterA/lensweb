from django.shortcuts import render
from rest_framework.views import APIView
from mathematics.wolfram import auto_solve, prove_equations, simplify_expression, solve_equations
from ocr import mathpix
from .wolfram import simplify_expression,solve_equations,auto_solve
# Create your views here.
class MathView(APIView):
    def post(self,request):
        # get data
        # validate subscription
        # pass query to wolfram
        query=mathpix.run_ocr(request.data['image'])
        if request.data['type']=='solve':     
            result,steps=solve_equations(query)
            #return response
            
        elif request.data['type']=='simplify':
            result,steps=simplify_expression(query)  
            #return response
        elif request.data['type']=='prove':
            result,steps=prove_equations(query)
        elif request.data['type']=='auto':
            answer=auto_solve(query)
            #return response
         