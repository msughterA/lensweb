import sys
import base64
import requests
import json
import os
from .serializers import OcrSerializer
import latex2mathml.converter
from wolframclient.evaluation import SecuredAuthenticationKey,WolframCloudSession
from wolframclient.language import wl,wlexpr
import re

APP_KEY=os.environ['OCR_APP_KEY']
APP_ID=os.environ['OCR_APP_ID']
#APP_KEY=''
#APP_ID=''
WOLFRAM_CLOUD_KEY=os.environ['WOLFRAM_CONSUMER_KEY']
WOLFRAM_CLOUD_SECRET=os.environ['WOLFRAM_CONSUMER_SECRET']


sak=SecuredAuthenticationKey(WOLFRAM_CLOUD_KEY,WOLFRAM_CLOUD_SECRET)
# initialize the wolfram
session=WolframCloudSession(credentials=sak)
# start the session
session.start()
# process query
def mathml_to_expression(mathml):
    mathml=str(mathml)
    expression=session.evaluate(wlexpr(f'''XML`MathML`MathMLToExpression[{mathml}]'''))
    print(expression)


def save_to_data_collection(image,text):
    data={'base64string':image,'text':text}
    serializer=OcrSerializer(data=data)
    #if serializer.is_valid(raise_exception=True):
    #    serializer.save() 
def ocr_response_format(result):
    '''
    :param json:
    :return the latex format of the text from the picture:
    '''
    latex_input=result.json()['text']
    ascii_text=text_parsing(result.json()['text'],result.json()['data'])
    print(result.json())
    print('THIS IS THE ASCII MATH')
    print(ascii_text)
    return result.json()['text']
def run_ocr(base64_img):
    image_uri = "data:image/jpg;base64," + base64_img
    try:
        r = requests.post("https://api.mathpix.com/v3/text",
            data=json.dumps({'src': image_uri,
                             "formats": ["text", "data", "html"],
                             # make mathpix to include only mathml in the data options
                             "data_options": {
                                "include_asciimath": True,
                             }
                             }),
            headers={"app_id": APP_ID, "app_key": APP_KEY,
                     "Content-type": "application/json"})
        text=ocr_response_format(r)
        save_to_data_collection(base64_img,text)
        return text
    except Exception as e:
        print(e)
        return 'error',False
        #abort(404, message="we are experiencing a technical issues with OCR please be patient")
pattern=r"\\(\()(.*?)(\))"       
def text_parsing(text,elements):
    class repl:
        def __init__(self):
            self.called = 0

        def __call__(self, match):
            self.called += 1
            return elements[self.called-1]

    ascii_text=re.sub(pattern,repl(),text)
    return ascii_text