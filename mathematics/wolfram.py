import requests
import wolframalpha
import urllib

APPID='PG3TTH-P3Q6Q5JRWX'
# Method for solving equations
def solve_equations(equation):
    query = urllib.parse.quote_plus(f"solve {equation}")
    query_url = f"http://api.wolframalpha.com/v2/query?" \
                f"appid={APPID}" \
                f"&input={query}" \
                f"&scanner=Solve" \
                f"&podstate=Result__Step-by-step+solution" \
                "&format=plaintext" \
                f"&output=json"

    r = requests.get(query_url).json()

    data = r["queryresult"]["pods"][0]["subpods"]
    result = data[0]["plaintext"]
    steps = data[1]["plaintext"]
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

    data = r["queryresult"]["pods"][0]["subpods"]
    result = data[0]["plaintext"]
    steps = data[1]["plaintext"]
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

    data = r["queryresult"]["pods"][0]["subpods"]
    result = data[0]["plaintext"]
    steps = data[1]["plaintext"]
    return steps,result

# Method for automatically answering math questions
def auto_solve(question):
    client = wolframalpha.Client(APPID)

    # Stores the response from
    # wolf ram alpha
    res = client.query(question)

    # Includes only text from the response
    answer = next(res.results).text
    return answer