from wolframclient.evaluation import SecuredAuthenticationKey,WolframCloudSession
from wolframclient.language import wl,wlexpr
import requests
import wolframalpha
import urllib
import os
import json
from py_asciimath.translator.translator import MathML2Tex
import re
from examples.views import *
import openai

openai.api_key=os.environ['OPEN_AI_KEY']
APPID=os.environ['WOLFRAM_APP_ID']

WOLFRAM_CLOUD_KEY=os.environ['WOLFRAM_CONSUMER_KEY']
WOLFRAM_CLOUD_SECRET=os.environ['WOLFRAM_CONSUMER_SECRET']

mathml2tex = MathML2Tex()
sak=SecuredAuthenticationKey(WOLFRAM_CLOUD_KEY,WOLFRAM_CLOUD_SECRET)
# initialize the wolfram
session=WolframCloudSession(credentials=sak)
# process query
def mathml_to_expression(mathml):
    # start the session
    session.start()
    mathml=str(mathml)
    expression=session.evaluate(wlexpr(f'''TeXForm[(sqrt(0.7) + sqrt(70))^2]'''))
    print(expression)
# get the url in the right format
def url_string(query,format):
    query = urllib.parse.quote_plus(f"{query}")
    query_url = f"http://api.wolframalpha.com/v2/query?" \
        f"appid={APPID}" \
        f"&input={query}" \
        f"&podstate=Result__Step-by-step+solution" \
        f"&format={format}" \
        f"&output=json"
    return query_url

# make a function to parse the json
def parse_json(json_data,key,query):
    #get the query result
    query_result=json_data['queryresult']
    #get the pods
    if 'pods' in query_result:
        pods=query_result['pods']
        # list to held the data element we are interested in
        data=[]
        for pod in pods:
            for subpod in pod['subpods']:
                if key in subpod:
                    d=subpod[key]
                    t=subpod[key].replace(r"""<math xmlns='http://www.w3.org/1998/Math/MathML'
    mathematica:form='StandardForm'
    xmlns:mathematica='http://www.wolfram.com/XML/'>""",repl)
                    #print(t)
                    try:
                        parsed = mathml2tex.translate(t, network=True, from_file=False, )
                        parsed = r'\( ' + parsed.strip('$') + r' \)'
                        data.append({'type':'latex','format':'tex','data':process_mathml_output(parsed)})
                    except:
                        print("An error occured")
                        data.append({'type': 'latex', 'format': 'tex', 'data': d})
                # print(parsed)
                #t=mathml2tex.translate(subpod[key], network=True, from_file=False,)
                #data.append(parsed)       
        return data
    else:
        try:
            data=[]
            # the process of solving the question with codex
            # 1. get the most similar questions from db and rank
            similar_questions_list, similar_diagrams_list,similar_answers_list=ranker(query)
            # 2. put them into a prompt script for codex to generate a rough solution
            # prompt_script=""" """
            # for i in range(len(similar_questions_list)):
            #     prompt_example=f'''#Question {i}: {similar_questions_list[i]}\n#Question {i} solution: {similar_answers_list[i]}'''
            #     prompt_script=prompt_script+'\n\n\n'+prompt_example
            #     if i==len(similar_questions_list)-1:
            #         prompt_script=prompt_script+'\n\n\n'+f'''#Question {i+1}: {query}\n#Question {i+1} solution:'''
            prompt_script=fine_tuned_script(similar_questions_list[0],similar_answers_list[0],similar_questions_list[4],similar_answers_list[4],run_parse2(query))        
            # 3. give the prompt to codex to generate the solution
            rough_solution=fine_tuned_response(prompt_script)
            # 4. put the rough solution into an execution prompt script to generate
            # the code the would give the solution
            #execution_script=f"""{prompt_script}\n\n\n{rough_solution}"""
            #print('THIS IS THE ROUGH SOLUTION {rough_solution}')
            #execution_script=generate_execution_script(query,rough_solution)
            # 5. run the executable script generated to get the solution
            #print(f'THIS IS THE EXECUTION_SCRIPT{execution_script}')
            #solution,err=exe(execution_script)
            data.append({'type':'latex','format':'tex','data':run_parse(rough_solution)})
            return data
        except Exception as e: 
            print(f'THIS IS THE ERROR THAT OCCURRED {e}')   
            data=[]
            print(f'THIS IS THE QUERY RESULT {query_result}')
            data.append({'type':'text','format':'txt','data':'Oooops we could not find an answer to your question'})
            data.append({'type':'text','format':'txt','data':'Try any of the following'})
            data.append({'type':'text','format':'txt','data':'(a) snapping the question properly'})
            data.append({'type':'text','format':'txt','data':'(b) Re-writing the question in a shorter form'})
            data.append({'type':'text','format':'txt','data':'(c) removing unnecessary details from the question'})
            return data

# Method for solving equations
def solve_equations(equation):
    query = urllib.parse.quote_plus(f"solve {equation}")
    query_url = url_string(query,'mathml')

    r = requests.get(query_url).json()

    try:
        data = r["queryresult"]["pods"][0]["subpods"]
        result = data[0]["mathml"]
        steps = data[1]["mathml"]
        return steps,result
    except:
        result="Ooooops we can't find a solution"
        steps=''    
        return steps,result

# Method for simplifying mathematical expressions
def simplify_expression(expression):
    query = urllib.parse.quote_plus(f"Simplify {expression}")
    query_url = f"http://api.wolframalpha.com/v2/query?" \
                f"appid={APPID}" \
                f"&input={query}" \
                f"&scanner=Simplify" \
                f"&podstate=Result__Step-by-step+solution" \
                "&format=plaintext" \
                f"&output=json"

    r = requests.get(query_url).json()

    try:
        data = r["queryresult"]["pods"][0]["subpods"]
        result = data[0]["plaintext"]
        steps = data[1]["plaintext"]
        return steps,result
    except:
        result="Ooooops we can't find a solution"
        steps=''    
        return steps,result

# Method for proving mathematical equations
def prove_equations(equation):
    query = urllib.parse.quote_plus(f"prove {equation}")
    query_url = f"http://api.wolframalpha.com/v2/query?" \
                f"appid={APPID}" \
                f"&input={query}" \
                f"&scanner=Prove" \
                f"&podstate=Result__Step-by-step+solution" \
                "&format=plaintext" \
                f"&output=json"

    r = requests.get(query_url).json()

    try:
        data = r["queryresult"]["pods"][0]["subpods"]
        result = data[0]["plaintext"]
        steps = data[1]["plaintext"]
        return steps,result
    except:
        result="Ooooops we can't find a solution"
        steps=''    
        return steps,result

# Method for automatically answering math questions
def auto_solve(question,format):
    #query = urllib.parse.quote_plus(f"{question}")
    query=question
    print(query)
    query_url=url_string(query,format)
    r = requests.get(query_url).json()
    
    return parse_json(r,format,query)

def convert_mathml(mathml_data):
    url='https://lensnode.herokuapp.com/api/v1/covertmathml'
    try:
        res=requests.post(url,mathml_data)
        if res.status_code==200:
            return res.json()
    except:
        print('An error occurred')
        return mathml_data     

pattern=r"""<math xmlns='http://www.w3.org/1998/Math/MathML'
                mathematica:form='StandardForm'
                xmlns:mathematica='http://www.wolfram.com/XML/'>"""
repl=r"""<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE math PUBLIC "-//W3C//DTD MathML 2.0//EN" "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd">
<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">"""

#  This is the latex question \( \int \sin x d x \)
# write a regex function to convert \mathrm{integral}
# '\\(  \\mathrm{integral}\\mathrm{sin}\\left(x\\right)dx=-\\mathrm{cos}\\left(x\\right)+\\mathrm{constant} \\)'
# replace \mathrm{integeral} with \int
def process_mathml_output(mathml_data):
    pattern=r'\\mathrm{integral}'
    repl=r'\\int'
    # replace \mathrm{integeral} with \int
    new_string=re.sub(pattern,repl,mathml_data)
    return new_string


'''
mathml2tex = MathML2Tex()
def convert_mathml(mathml_data):
    try:
       mathml_data=mathml_data.replace(r"""<math xmlns='http://www.w3.org/1998/Math/MathML'
    mathematica:form='StandardForm'
    xmlns:mathematica='http://www.wolfram.com/XML/'>""",repl,mathml_data)   
       parsed=mathml2tex.translate(mathml_data, network=True, from_file=False,)
       parsed=r'\( ' +parsed.strip('$') +r' \)'
       #print()
       return parsed
    except:
       return mathml_data  
'''  
def get_response_rough(prompt):
       
        #prompt=format_prompt(prompt)
        return openai.Completion.create(
          engine="text-davinci-002",
          prompt=prompt,
          temperature=0,
          max_tokens=600,
          top_p=1.0,
          frequency_penalty=0.0,
          presence_penalty=0.0,
        stop=['\n\n\n#']
        )['choices'][0]['text']
# method to generate the code for the solution        
def program_response(prompt):
        # code-davinci-002
        # text-davinci-002
        # text-curie-001
        # text-babbage-001
        # text-ada-001
        #prompt=format_prompt(prompt)
        return openai.Completion.create(
          engine="text-ada-001",
          prompt=prompt,
          temperature=0,
          max_tokens=1000,
          top_p=1.0,
          frequency_penalty=0.0,
          presence_penalty=0.0,
        )['choices'][0]['text']    
        
def generate_execution_script(problem,solution):
    execution_script=f"""
import re
import sympy as sp
import numpy as np

'''
#Question: {problem}
'''
'''
write a program to find the solution to the question above
'''
    """  
    gpt3_code=program_response(execution_script)   
    return execution_script+gpt3_code     
def fine_tuned_script(q1,a1,q2,a2,p):
    f_script=f"""\n        <question>\n        <problem>\n        {q1}
        \n        <\/problem>\n        <solution>\n       {a1}
        \n        <\/solution>\n        <\/question>\n        <question>\n        <problem>\n        {q2}
        \n        <\/problem>\n        <solution>\n       {a2}        <\/solution>\n        <\/question>\n        <question>\n        <problem>\n        {p}\n        <\/problem>\n        <solution>\n        
        """+r'\n\n###\n\n'
    return f_script    
def fine_tuned_response(p):
    print(f'This is the prompt {p}')
    a=openai.Completion.create(
    model='curie:ft-personal-2022-06-28-17-55-02',
    prompt=p,
    temperature=0,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    )
    print(f'This is the finetuned response {a}')
    return a['choices'][0]['text']
def ranking(query):
      similar_questions_list, similar_diagrams_list,similar_answers_list=ranker(query)   
# the process of solving the question with codex
# 1. get the most similar questions from db and rank
# 2. put them into a prompt script for codex to generate a rough solution
# 3. put the rough solution into an execution prompt script to generate 
# the code the would give the solution
# 4. run the executable script generated to get the solution
def exe(code):
    import sys
    import io

    # create file-like string to capture output
    codeOut = io.StringIO()
    codeErr = io.StringIO()

    # capture output and errors
    sys.stdout = codeOut
    sys.stderr = codeErr

    exec(code)

    # restore stdout and stderr
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    return codeOut,codeErr
