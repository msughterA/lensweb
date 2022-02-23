import requests
import wolframalpha
import urllib
import os

#from mathematics.wolfram import APPID

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

#make a function to parse the json
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
                    data.append({'type':'text','format':'txt','data':subpod[key]})
        return data
    else:
        data=[]
        data.append({'type':'text','format':'txt','data':'Oooops we could not find an answer to your question'})
        data.append({'type':'text','format':'txt','data':'Try any of the following'})
        data.append({'type':'text','format':'txt','data':'(a) snapping the question properly'})
        data.append({'type':'text','format':'txt','data':'(b) Re-writing the question in a shorter form'})
        data.append({'type':'text','format':'txt','data':'(c) removing unnecessary details from the question'})
        return data
# Method for balancing chemical equations
def balance_equation(equation):
    pass

# Name chemical compound
def name_compound(compound):
    pass

def auto_solve(question,format):
    #query = urllib.parse.quote_plus(f"{question}")
    query=question
    query_url=url_string(query,format)
    r = requests.get(query_url).json()
    return parse_json(r,format)
