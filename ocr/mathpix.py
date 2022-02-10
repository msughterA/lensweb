import sys
import base64
import requests
import json
import os
from .serializers import OcrSerializer


#APP_KEY=os.environ['OCR_APP_KEY']
#APP_ID=os.environ['OCR_APP_ID']
APP_KEY=''
APP_ID=''



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
    text = json.loads(result.text)
    return text['text']
def run_ocr(base64_img):
    image_uri = "data:image/jpg;base64," + base64_img
    try:
        r = requests.post("https://api.mathpix.com/v3/text",
            data=json.dumps({'src': image_uri,
                             "formats": ["text", "data", "html"],
                             "data_options": {
                                 "include_asciimath": True,
                                 "include_latex": True  
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

