import base64
from cProfile import run
from django.shortcuts import redirect, render
from .forms import AdminLogInForm, UploadFileForm
from .models import (
    Question,
    Collection,
    Answer,
    AnswerText,
    QuestionText,
    QuestionDiagram,
    AnswerDiagram,
)
from django.views.decorators.http import require_POST
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sklearn.metrics.pairwise import cosine_similarity
from .utils import CacheData
import numpy as np
import tensorflow_hub as hub
import json
from enum import Enum
from ocr import mathpix
import pickle
import ast
import re
import requests


# Number of Examples
NUMBER_OF_EXAMPLES = 5
# subjects
class subjects(Enum):
    mathematics = 1
    physics = 2
    chemistry = 3
    biology = 4


# Cache data instance

cache_data = CacheData()


def get_questions_and_embeddings():

    collections = Collection.objects.all()
    # loop over all the collections to get all the questions with their diagrams
    for colllection in collections:
        questions = Question.objects.filter(id=colllection.id)
        for question in questions:
            # texts = question.text_set.all()
            # diagrams = question.diagram_set.all()
            # texts would store dictionaries textId, questionId,
            # text embedding would be stored in text_embeddings
            # for text in texts:
            # text_dict = {}
            cache_data.append_data(
                question_id=question.id, text_embedding=question.text_embedding
            )


# get_questions_and_embeddings()

# Load the embedding module
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
# EMBED_DIR=r'C:\\Users\\AYERHAN MSUGHTER\\Desktop\\Enigma\\module_useT'
# embed=hub.load(EMBED_DIR)


def embed_question(data):
    embedding = embed([data])
    # embedding=[]
    return embedding


def get_top_n_most_similar_questions_with_answers_similarites(embedding):
    similarities = cosine_similarity(embedding, np.array(cache_data.text_embeddings))
    # unique_ids = []
    # votes = []
    # for id,vote in zip(cache_data.text_ids,similarities):
    #     if id not in unique_ids:
    #         unique_ids.append(id)
    #         votes.append(vote)
    #     else:
    #         id_index = unique_ids.index(id)
    #         votes[id_index] = votes[id_index]+vote

    return similarities


def ranker(query):
    embedded_question = embed_question(query)
    similarity_list = get_top_n_most_similar_questions_with_answers_similarites(
        embedded_question
    )
    idx = np.argpartition(
        similarity_list[0],
        -NUMBER_OF_EXAMPLES,
    )[-NUMBER_OF_EXAMPLES:]
    indices = idx[np.argsort((-similarity_list[0])[idx])]
    questions_and_answers = []
    for i, index in enumerate(indices):
        qa_dict = {}
        question_texts = []
        question_diagrams = []
        answer_texts = []
        answer_diagrams = []
        # print(f'THE CLOSEST QUESTION IS {questions[index]}')
        question_id = cache_data.text_ids(index)
        question = Question.objects.get(id=question_id)
        answer = Answer.objects.get(question_id=question_id)
        qa_dict["questionMap"] = question.map
        qa_dict["answerMap"] = answer.map
        # get all question texts for this question
        for text in question.questiontext_set.all():
            question_texts.append(text.question_text)
        # get all question diagrams for this question
        for diagram in question.questiondiagram_set.all():
            question_diagrams.append(diagram.base64string)
        # get all answer texts for the answer to the question
        for text in answer.answertext_set.all():
            answer_texts.append(text.answer_text)
        # get all answer diagrams for the answer to the question
        for diagram in answer.answerdiagram_set.all():
            answer_diagrams.append(diagram.base64string)

        qa_dict["questionTexts"] = question_texts
        qa_dict["questionDiagrams"] = question_diagrams
        qa_dict["answerDiagrams"] = answer_diagrams
        qa_dict["answerTexts"] = answer_texts

        questions_and_answers.append(qa_dict)
    return questions_and_answers


img_pattern = "<img>(.*?)</img>"
link_pattern = "(?:http\:|https\:)?\/\/.*\.(?:png|jpg)"


class DeleteQuestionView(APIView):
    def post(self, request):
        quesion_id = request.data["questionId"]
        if Question.objects.filter(id=quesion_id):
            return Response(
                data={"message": "question does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            # while deleting make sure to delete the entire collection
            # if the question your deleting is the last in it
            question = Question.objects.filter(id=quesion_id).get()
            collection = question.collection
            question.delete()
            if collection.length == 1:
                collection.delete()
            else:
                collection.length = collection.length - 1
                # call the function to update the collections database
                collection.save()
            return Response(
                data={"message": "Question deleted successfully"},
                status=status.HTTP_200_OK,
            )


class UserView(APIView):
    def post(self, request):
        """handle client requests for examples to questions
        Args:
            request (json): The query question {'question':'','subjectindex':[0-5]}
        """
        query, ascii_text = mathpix.run_ocr(request.data["image"])
        similar_questions_and_answers = ranker(query)
        return Response(
            data={"examples": similar_questions_and_answers}, status=status.HTTP_200_OK
        )

    def get(self, request):
        questions_and_answers = []
        questions = Question.objects.all()
        for i, question in enumerate(questions):
            qa_dict = {}
            question_texts = []
            question_diagrams = []
            answer_texts = []
            answer_diagrams = []
            # print(f'THE CLOSEST QUESTION IS {questions[index]}')
            question_id = question.id
            question = Question.objects.get(id=question_id)
            answer = Answer.objects.get(question_id=question_id)
            qa_dict["questionMap"] = question.map
            qa_dict["answerMap"] = answer.map
            # get all question texts for this question
            for text in question.questiontext_set.all():
                question_texts.append(text.text)
            # get all question diagrams for this question
            for diagram in question.questiondiagram_set.all():
                question_diagrams.append(diagram.base64string)
            # get all answer texts for the answer to the question
            for text in answer.answertext_set.all():
                answer_texts.append(text)
            # get all answer diagrams for the answer to the question
            for diagram in answer.answerdiagram_set.all():
                answer_diagrams.append(diagram)

            qa_dict["questionTexts"] = question_texts
            qa_dict["questionDiagrams"] = question_diagrams
            qa_dict["answerDiagrams"] = answer_diagrams
            qa_dict["answerTexts"] = answer_texts

            questions_and_answers.append(qa_dict)
        return Response(
            data={"all questions": questions_and_answers}, status=status.HTTP_200_OK
        )


def post(self, request):
    query, ascii_text = mathpix.run_ocr(request.data["image"])
    response = requests.post("https://lensai.herokuapp.com/embedder/embedder")
    return Response(
        data={"message": "This Feature Has not yet been enable"},
        status=status.HTTP_401_UNAUTHORIZED,
    )


pattern = r"((?<!\$)\${1,2}(?!\$)(.*?)(?<!\$)\${1,2}(?!\$))"


class repl:
    def __init__(self):
        self.called = 0

    def __call__(self, match):
        self.called += 1
        print(match.group(0).strip("$"))
        return r"\( " + match.group(0).strip("$") + r" \)"


pattern2 = r"\\(\()(.*?)(\\\))"
# def text_parsing(text,elements):
class repl2:
    def __init__(self):
        self.called = 0

    def __call__(self, match):
        self.called += 1
        # parenthesis to ascii equations
        a = match.group(0).strip(r"\(")
        a = a.strip(r"\)")
        return r"$" + a + r"$"


def run_parse(t):
    a = re.sub(pattern, repl(), t)
    a = re.sub(r"\\begin\{align\*\}", r"\( \\begin{align*}", a)
    a = re.sub(r"\\end\{align\*\}", r"end{align*} \)", a)
    # a=re.sub(r'\\\[',r'\( \[',a)
    # a=re.sub(r'\\\]',r'\] \)',a)
    return a


def run_parse2(t):
    a = re.sub(pattern2, repl2(), t)
    return a
