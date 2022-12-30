from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import FileReceive, FileSend
from .models import Question, Collection, Answer, AnswerText, QuestionText
import json
import os

MEDIA_DIR = ""
FILE_SEND_COLLECTION = os.path.join(MEDIA_DIR, "filesend/collections")
FILE_SEND_QUESTION_AND_ANSWER = os.path.join(MEDIA_DIR, "filesend/questionAndAnswer")
FILE_RECEIVE_COLLECTION = os.path.join(MEDIA_DIR, "filereceive/collections")
FILE_RECEIVE_QUESTION_AND_ANSWER = os.path.join(
    MEDIA_DIR, "filereceive/questionAndAnswer"
)

# utility functions
def getCollection(id):
    collection = Collection.objects.get(id=id)
    questions = collection.question_set.all()
    questions_and_answers = []
    collection_json = {}
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
    collection_json["questionsAndAnswers"] = questions_and_answers
    collection_json["school"] = collection.school
    collection_json["year"] = collection.year
    collection_json["postedBy"] = collection.postedBy.id
    collection_json["type"] = "collection"
    return collection_json


def getQuestionAndAnswer(id):
    qa_dict = {}
    collection_json = {}
    question_and_answer = []
    question_texts = []
    question_diagrams = []
    answer_texts = []
    answer_diagrams = []
    # print(f'THE CLOSEST QUESTION IS {questions[index]}')
    question_id = id
    collection = Collection.objects.get(question_id=id)
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

    question_and_answer.append(qa_dict)
    collection_json["questionsAndAnswers"] = question_and_answer
    collection_json["school"] = collection.school
    collection_json["year"] = collection.year
    collection_json["postedBy"] = collection.postedBy.id
    collection_json["type"] = "questionAndAnswer"

    return collection_json


def check_collection_exists(id):
    # try except logic
    try:
        collection = Collection.objects.get(pk=id)
        return True
    except Collection.DoesNotExist:
        return False


def check_question_and_answer_exists(id):
    # try except logic
    try:
        question = Question.objects.get(pk=id)
        return True
    except Question.DoesNotExist:
        return False


# Create your views here.
class FileReceiveView(APIView):
    def post(self, request):
        filetype = request.data["type"]
        fileId = request.data["fileId"]
        userId = request.data["userId"]
        if filetype == "collection":
            # create a file at media/filereceive/collections/userId_fileId.json
            filepath = os.path.join(FILE_RECEIVE_COLLECTION, f"{userId}_{fileId}.json")
            with open(filepath, "w") as f:
                print("json send file created")

        else:
            # create a file at media/filereceive/collections/userId_fileId.json
            filepath = os.path.join(
                FILE_RECEIVE_QUESTION_AND_ANSWER, f"{userId}_{fileId}.json"
            )
            with open(filepath, "w") as f:
                print("json reception file created")
        return Response(
            {
                "message": "success",
                "data": {"socket": f"ws/filereceive/{userId}/{fileId}"},
            },
            status=status.HTTP_200_OK,
        )


class FileSendView(APIView):
    def post(self, request):
        filetype = request.data["type"]
        fileId = request.data["fileId"]
        userId = request.data["userId"]
        if filetype == "collection":
            if not check_collection_exists(id):
                return Response(
                    {"message": "File does not exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            collection_json = getCollection(fileId)
            # write the json file to media/filesend/collections/userId_fileId.txt
            filepath = os.path.join(FILE_SEND_COLLECTION, f"{userId}_{fileId}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(collection_json, f, ensure_ascii=False, indent=4)

        else:
            if not check_question_and_answer_exists(id):
                return Response(
                    {"message": "File does not exists"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            collection_json = getQuestionAndAnswer(fileId)
            # write the json file media/filesend/questionAndAnswer/userId_fileId.txt
            filepath = os.path.join(
                FILE_SEND_QUESTION_AND_ANSWER, f"{userId}_{fileId}.json"
            )
            with open(filepath, "w") as f:
                json.dump(collection_json, f, ensure_ascii=False, indent=4)
        return Response(
            {
                "message": "Success",
                "data": {"socket": f"ws/filesend/{userId}/{fileId}/{0}"},
            },
            status=status.HTTP_200_OK,
        )
