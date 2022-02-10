import base64
from django.shortcuts import redirect, render
from .forms import AdminLogInForm, UploadFileForm
from .models import Question,Diagram
from django.views.decorators.http import require_POST
from .serializers import QuestionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
#import tensorflow_hub as hub
import json
from enum import Enum
from ocr import mathpix
import pickle
import ast
import re


# Number of Examples
NUMBER_OF_EXAMPLES=2
# subjects
class subjects(Enum):
    mathematics=1
    physics=2
    chemistry=3
    biology=4

# Create your views here.
def index(request):
    adminLogInForm=AdminLogInForm()
    context={'adminLogInForm':adminLogInForm}
    return render(request,'examples/index.html',context)

@require_POST
def adminLogin(request):
    adminLogInForm=AdminLogInForm(request.POST)
    context={}
    # if  the credentials are valid
    if adminLogInForm.is_valid():
        email=request.POST['email']
        password=request.POST['password']
    # Render the adminView
    # Display an Error on the form
    return render(request,'examples/uploadfile.html',context)


@require_POST
def adminUpload(request):
    form = UploadFileForm(request.POST, request.FILES)
    
    context={'form':form}
    if form.is_valid():
       file= request.FILES['file']
       json_file=json.load(file)
       data = json_file['questions']
      # print(json_file[0])
       if '.txt' not in file.name:
            redirect('uploadfile.html')
       serializer=QuestionSerializer(data=data,many=True)
       if serializer.is_valid(raise_exception=True):
           serializer.save()    
        
    return render(request,'examples/uploadfile.html')   


def get_questions_and_embeddings(subject):
    """Fetch the questions and embedding for a subject

    Args:
        subject (string): the name of the subject you would like to get
    """
    #questions=Question.objects.filter(subject__iexact=subject)
    #questions=Question.objects.all()
    questions=[]
    questions_list=[]
    embeddings_list=[]
    answers_list=[]
    diagrams_list=[]
    for question in questions:
        # Get the quesion text
        questions_list.append(question.text)
        # Get the question embedding
        # make sure to decode the binary field
        embeddings_list.append(ast.literal_eval(question.embedding))
        # Get the answer
        answers_list.append(question.answer)
        # Get the diagrams
        diagrams_list.append(question.diagram_set.all())
        
    return questions_list,np.array(embeddings_list), answers_list,diagrams_list


# get Mathematical questions, embeddings and diagrams
math_questions,math_embeddings,math_answers,math_diagrams=get_questions_and_embeddings('mathematics')

# Load the embedding module
#embed=hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
EMBED_DIR=r'C:\\Users\\AYERHAN MSUGHTER\\Desktop\\Enigma\\module_useT'
#embed=hub.load(EMBED_DIR)

def embed_question(data):
    #embedding=embed([data])
    embedding=[]
    return embedding
def get_top_n_most_similar_questions_with_answers_similarites(embedding,q_embeddings):
    print(len(q_embeddings))
    print(f'print embedding shape {np.shape(embedding)}')
    print(f'print q_embedding shape {np.shape(q_embeddings)}')
    similarities=cosine_similarity(embedding, q_embeddings)
    return similarities
def ranker(query):
    embedded_question = embed_question(query)
    similarity_list = get_top_n_most_similar_questions_with_answers_similarites(embedded_question, math_embeddings)
    idx = np.argpartition(similarity_list[0], -NUMBER_OF_EXAMPLES, )[-NUMBER_OF_EXAMPLES:]
    indices = idx[np.argsort((-similarity_list[0])[idx])]
    similar_questions_list = []
    similar_questions_list_1=[]
    similar_answers_list = []
    similar_answers_list_1=[]
    similar_diagrams_list=[]
    similar_diagrams_list_1=[]
    for index in indices:
        #print(f'THE CLOSEST QUESTION IS {questions[index]}')
        similar_questions_list.append(math_questions[index])
        similar_questions_list_1.append(math_questions[index])
        similar_answers_list_1.append(math_answers[index])
        similar_diagrams_list_1.append(math_diagrams[index])
    similar_questions_list=list(dict.fromkeys(similar_questions_list))
    for item in similar_questions_list:
        indx=similar_questions_list_1.index(item)
        #similar_answers_list = list(dict.fromkeys(similar_answers_list))
        similar_answers_list.append(similar_answers_list_1[indx])
        similar_diagrams_list.append(similar_diagrams_list_1[indx])
    return similar_questions_list,similar_diagrams_list,similar_answers_list
    

img_pattern='<img>(.*?)</img>'
link_pattern='(?:http\:|https\:)?\/\/.*\.(?:png|jpg)'
        
class UserView(APIView):
    def post(self,request):
        """handle client requests for examples to questions

        Args:
            request (json): The query question {'question':'','subjectindex':[0-5]}
        """
        query=mathpix.run_ocr(request.data['image'])
        similar_questions_list, similar_diagrams_list,similar_answers_list=ranker(query)
        # Iterate through the lists
        examples=[]
        for i in range(len(similar_questions_list)):
            example={}
            example['question']=similar_questions_list[i]
            #example['diagrams']=similar_diagrams_list[i]
            example['answer']=similar_answers_list[i]
            examples.append(example)
        request_examples=[]    
        for i in range(len(examples)):
              example={}
              question=examples[i]['question']
              answer=examples[i]['answer']
              diagrams_list=re.findall(link_pattern,question) 
              question=re.sub(img_pattern,'',question) 
              question_and_answer=question + '\n' + answer 
              ex=[]
              if diagrams_list:
                  for dig in diagrams_list:
                      dig_dict={'type':'image','format':'jpg','data':dig}
                      ex.append(dig_dict)
              ex.append({'type':'latex','format':'tex','data':question_and_answer})        
              example['example']=ex 
              request_examples.append(example)    
        return Response(data={'examples':request_examples},status=status.HTTP_200_OK)    
    
    def get(self,request):
        questions=Question.objects.all()
        diagrams=Diagram.objects.all()
        examples=[]
        for i,question in enumerate(questions):
            example={}
            example['question']=question.text
            example['answer']=question.answer
            #example['diagrams']=question.diagram_set.all()
            examples.append(example)
        request_examples=[]    
        for i in range(len(examples)):
              example={}
              question=examples[i]['question']
              answer=examples[i]['answer']
              diagrams_list=re.findall(link_pattern,question) 
              question=re.sub(img_pattern,'',question) 
              question_and_answer='Question'+'\n'+question + '\n' + 'Answer' + answer 
              ex=[]
              if diagrams_list:
                  for dig in diagrams_list:
                      dig_dict={'type':'image','format':'jpg','data':dig}
                      ex.append(dig_dict)
              ex.append({'type':'latex','format':'tex','data':question_and_answer})         
              example['example']=ex 
              request_examples.append(example)
              
        return Response(data={'examples':request_examples},status=status.HTTP_200_OK)