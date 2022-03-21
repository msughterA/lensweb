import requests
import wolframalpha
import urllib
import os
import json


APPID=os.environ['WOLFRAM_APP_ID']

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
                    #data.append(subpod[key])
                    d=subpod[key]
                    data.append({'type':'latex','format':'tex','data':d})
        convert_mathml(data)           
        #return data
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
        return mathml_data     