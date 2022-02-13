import requests
import wolframalpha
import urllib
import os

APPID=os.environ['WOLFRAM_APP_ID']
#APPID=''


# get the url in the right format
def url_string(query,format):
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
    pods=query_result['pods']
    # list to held the data element we are interested in
    data=[]
    for pod in pods:
        for subpod in pod['subpods']:
            if key in subpod:
                #data.append(subpod[key])
                data.append({'type':'latex','format':'tex','data':subpod[key]})
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
    query = urllib.parse.quote_plus(f"{question}")
    query_url=url_string(query,format)
    r = requests.get(query_url).json()
    return parse_json(r,format)