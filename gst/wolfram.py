from wolframclient.evaluation import SecuredAuthenticationKey,WolframCloudSession
from wolframclient.language import wl,wlexpr
import requests
import wolframalpha
import urllib
import os
import json
from py_asciimath.translator.translator import MathML2Tex
import re

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
                   d=subpod[key]
                   data.append({'type':'text','format':'txt','data':d})
                # print(parsed)
                #t=mathml2tex.translate(subpod[key], network=True, from_file=False,)
                #data.append(parsed)       
        return True,data
    else:
        
        return False,[]
    
# Method for automatically answering General knowledge questions
def wolfram_answer(question,format):
    #query = urllib.parse.quote_plus(f"{question}")
    query=question
    print(query)
    query_url=url_string(query,format)
    r = requests.get(query_url).json()
    
    return parse_json(r,format)    