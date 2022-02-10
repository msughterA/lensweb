import requests
import wolframalpha
import urllib
import os
#from mathematics.wolfram import APPID

#APPID=os.environ['WOLFRAM_APP_ID']
APPID=''
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
    pods=query_result['pods']
    # list to held the data element we are interested in
    data=''
    for pod in pods:
        for subpod in pod['subpods']:
            if key in subpod:
                #data.append(subpod[key])
                data=data+'\n'+str(subpod[key])
    return data

# Method for balancing chemical equations
def balance_equation(equation):
    pass

# Name chemical compound
def name_compound(compound):
    pass

def auto_solve(question,format):
    query = urllib.parse.quote_plus(f"{question}")
    query_url=url_string(query,format)
    r = requests.get(query_url).json()
    return parse_json(r,format)
