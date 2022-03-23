from wolframclient.evaluation import SecuredAuthenticationKey,WolframCloudSession
from wolframclient.language import wl,wlexpr
import requests
import wolframalpha
import urllib
import os
import json
from py_asciimath.translator.translator import MathML2Tex

APPID=os.environ['WOLFRAM_APP_ID']

WOLFRAM_CLOUD_KEY=os.environ['WOLFRAM_CONSUMER_KEY']
WOLFRAM_CLOUD_SECRET=os.environ['WOLFRAM_CONSUMER_SECRET']

mathml2tex = MathML2Tex()
sak=SecuredAuthenticationKey(WOLFRAM_CLOUD_KEY,WOLFRAM_CLOUD_SECRET)
# initialize the wolfram
session=WolframCloudSession(credentials=sak)

# Replacement text
repl=r"""<?xml version='1.0' encoding='UTF-8'?>
<!DOCTYPE math PUBLIC "-//W3C//DTD MathML 2.0//EN" "http://www.w3.org/Math/DTD/mathml2/mathml2.dtd">
<math xmlns="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">"""

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
def parse_json(json_data,key):
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
                    t=subpod[key].replace(r"""<math xmlns='http://www.w3.org/1998/Math/MathML'
    mathematica:form='StandardForm'
    xmlns:mathematica='http://www.wolfram.com/XML/'>""",repl)
                try:
                    parsed = mathml2tex.translate(t, network=True, from_file=False, )
                    parsed = r'\( ' + parsed.strip('$') + r' \)'
                    data.append({'type':'latex','format':'tex','data':parsed})
                except:
                    print("An error occured")
                    data.append({'type': 'latex', 'format': 'tex', 'data': t})
                # print(parsed)
                #t=mathml2tex.translate(subpod[key], network=True, from_file=False,)
                #data.append(parsed)       
        return data
    else:
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
    
    return parse_json(r,format)

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