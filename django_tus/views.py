import base64
import logging
from rest_framework import generics
from django.http import HttpResponse
from wsgiref.util import FileWrapper

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from rest_framework import generics
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from django_tus.conf import settings
from django_tus.response import TusResponse
from django_tus.signals import tus_upload_finished_signal
from django_tus.tusfile import TusFile, TusChunk, FilenameGenerator
from pathvalidate import is_valid_filename
from examples.models import (
    Question,
    Collection,
    Answer,
    AnswerText,
    QuestionText,
    QuestionDiagram,
    AnswerDiagram,
)
from examples.utils import CacheData
import os
import tensorflow_hub as hub
import json
from django.conf import settings
from threading import Thread
from lensweb import celery_app

logger = logging.getLogger(__name__)

TUS_SETTINGS = {}

# get_questions_and_embeddings()

# Load the embedding module
embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
# EMBED_DIR=r'C:\\Users\\AYERHAN MSUGHTER\\Desktop\\Enigma\\module_useT'
# embed=hub.load(EMBED_DIR)


def embed_question(data):
    embedding = embed([data])
    # embedding=[]
    return embedding


@celery_app.task()
def unpack_json_upload(filepath):
    f = open(filepath, "r")
    uploaded_json = json.load(f)
    # TODO complete the if method == edit part of the function
    method = uploaded_json["method"]
    if method == "edit":
        # a client should be able to edit only one question at a time
        # they can either delete it completely or edit one of the following
        part = uploaded_json["part"]
        # the question part
        if part == "question":
            question_id = uploaded_json["questionId"]
            if Question.objects.filter(id=question_id):
                # rewrite the entire data to avoid confusion
                question = Question.objects.filter(id=question_id).get()
                # for this part the data list contains only one quesion
                # which is the question to be edited
                question_and_answer_list = uploaded_json["data"]
                for qa in question_and_answer_list:
                    # create the Question model with the map , text_embedding
                    concatenatedText = qa["concatenatedText"]
                    question_map = qa["questionMap"]
                    question_embedding = embed_question(concatenatedText)
                    question.text_map(question_embedding)
                    cacheData = CacheData()
                    cacheData.edit_data(
                        question_id=question_id, new_text_embedding=question_id
                    )
                    question.text_embedding = question_embedding
                    question.save()
                    # delete all the questionTexts related to these question
                    QuestionText.objects.filter(question_id=question.id).delete()
                    # loop through all the question text and save them to DB
                    questionTexts = qa["questionTexts"]
                    for qt in questionTexts:
                        questionText = QuestionText(
                            question_text=qt["text"], question=question
                        )
                        questionText.save()
                    # delete all the diagrams related to the questions
                    QuestionDiagram.objects.filter(question_id=question.id).delete()
                    # write the new diagrams to data base
                    questionDiagrams = qa["questionDiagrams"]
                    for qd in questionDiagrams:
                        questionDiagram = QuestionDiagram(
                            base64string=qd["diagram"], question=question
                        )
                        questionDiagram.save()

        else:
            answer_id = uploaded_json["answerId"]
            question_id = uploaded_json["questionId"]
            if Answer.objects.filter(id=answer_id) and Question.objects.filter(
                id=question_id
            ):
                question = Question.objects.filter(id=question_id).get()
                question_and_answer_list = uploaded_json["data"]
                for qa in question_and_answer_list:
                    # get the major details for the answer
                    answer_map = qa["answerMap"]
                    # create the answer object
                    answer = Answer.objects.filter(id=answer_id).get()
                    answer.answer_map = answer_map
                    answer.save()
                    # delete all the answerTexts related to these answer
                    AnswerText.objects.filter(question_id=question.id).delete()
                    # loop through all the answer text and save them to DB
                    answerTexts = qa["answerTexts"]
                    for at in answerTexts:
                        answerText = AnswerText(answer_text=at["text"], answer=answer)
                        answerText.save()
                    # delete all the diagrams related to the answer
                    AnswerDiagram.objects.filter(question_id=question.id).delete()
                    answerDiagrams = qa["answerDiagrams"]
                    for ad in answerDiagrams:
                        answerDiagram = AnswerDiagram(
                            answer=answer, base64string=ad["diagram"]
                        )
                        answerDiagram.save()

    # elif method == "delete":
    #     pass
    else:
        postedBy = uploaded_json["postedBy"]
        school = uploaded_json["school"]
        year = uploaded_json["year"]
        length = uploaded_json["lenght"]
        collection = Collection(
            postedBy=postedBy, school=school, year=year, length=length
        )
        collection.save()
        # get the list of questions and answers
        question_and_answer_list = uploaded_json["data"]
        for qa in question_and_answer_list:
            # create the Question model with the map , text_embedding
            concatenatedText = qa["concatenatedText"]
            question_map = qa["questionMap"]
            question_embedding = embed_question(concatenatedText)
            # create the question object
            question = Question(
                text_map=question_map,
                text_embedding=json.dumps(question_embedding),
                collection=collection,
            )
            cacheData = CacheData()
            cacheData.append_data(
                question_id=question.id, text_embedding=question_embedding
            )
            question.save()
            # loop through all the question text and save them to DB
            questionTexts = qa["questionTexts"]
            for qt in questionTexts:
                questionText = QuestionText(question_text=qt["text"], question=question)
                questionText.save()
            questionDiagrams = qa["questionDiagrams"]
            for qd in questionDiagrams:
                questionDiagram = QuestionDiagram(
                    base64string=qd["diagram"], question=question
                )
            # get the major details for the answer
            answer_map = qa["answerMap"]
            # create the answer object
            answer = Answer(
                question=question, answer_map=answer_map, collection=collection
            )
            answer.save()
            # loop through all the answer text and save them to DB
            answerTexts = qa["answerTexts"]
            for at in answerTexts:
                answerText = AnswerText(answer_text=at["text"], answer=answer)
                answerText.save()
            answerDiagrams = qa["answerDiagrams"]
            for ad in answerDiagrams:
                answerDiagram = AnswerDiagram(answer=answer, base64string=ad["diagram"])
                answerDiagram.save()
    f.close()
    os.remove(filepath)


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
        qa_dict["questionMap"] = question.text_map
        qa_dict["answerMap"] = answer.text_map
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
    collection_json["questionsAndAnswers"] = questions_and_answers
    collection_json["school"] = collection.school
    collection_json["year"] = collection.year
    collection_json["postedBy"] = collection.postedBy.id
    # collection_json["type"] = "collection"
    return collection_json


def pack(userId, deviceId, fileId):
    collection_json = getCollection(fileId)
    FILE_STORAGE_PATH = os.path.join(settings.BASE_DIR, "downloads")
    # Check whether the specified path exists or not
    isExist = os.path.exists(FILE_STORAGE_PATH)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(FILE_STORAGE_PATH)
    filepath = os.path.join(FILE_STORAGE_PATH, f"{userId}_{deviceId}_{fileId}.json")
    with open(filepath, "w") as f:
        json.dump(collection_json, f)
    return filepath


class TusUpload(View):
    on_finish = None

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):

        if not self.request.META.get("HTTP_TUS_RESUMABLE"):
            return TusResponse(status=405, content="Method Not Allowed")

        override_method = self.request.META.get("HTTP_X_HTTP_METHOD_OVERRIDE")
        if override_method:
            self.request.method = override_method

        return super(TusUpload, self).dispatch(*args, **kwargs)

    def finished(self):
        if self.on_finish is not None:
            self.on_finish()

    def get_metadata(self, request):
        metadata = {}
        if request.META.get("HTTP_UPLOAD_METADATA"):
            for kv in request.META.get("HTTP_UPLOAD_METADATA").split(","):
                splited_metadata = kv.split(" ")
                if len(splited_metadata) == 2:
                    key, value = splited_metadata
                    value = base64.b64decode(value)
                    if isinstance(value, bytes):
                        value = value.decode()
                    metadata[key] = value
                else:
                    metadata[splited_metadata[0]] = ""
        return metadata

    def options(self, request, *args, **kwargs):
        return TusResponse(status=204)

    def post(self, request, *args, **kwargs):

        metadata = self.get_metadata(request)

        metadata["filename"] = self.validate_filename(metadata)

        message_id = request.META.get("HTTP_MESSAGE_ID")
        if message_id:
            metadata["message_id"] = base64.b64decode(message_id)

        if (
            settings.TUS_EXISTING_FILE == "error"
            and settings.TUS_FILE_NAME_FORMAT == "keep"
            and TusFile.check_existing_file(metadata.get("filename"))
        ):
            return TusResponse(status=409, reason="File with same name already exists")

        file_size = int(
            request.META.get("HTTP_UPLOAD_LENGTH", "0")
        )  # TODO: check min max upload size

        tus_file = TusFile.create_initial_file(metadata, file_size)

        return TusResponse(
            status=201,
            extra_headers={
                "Location": "{}{}".format(
                    request.build_absolute_uri(), tus_file.resource_id
                )
            },
        )

    def head(self, request, resource_id):

        tus_file = TusFile.get_tusfile_or_404(str(resource_id))

        return TusResponse(
            status=200,
            extra_headers={
                "Upload-Offset": tus_file.offset,
                "Upload-Length": tus_file.file_size,
            },
        )

    def patch(self, request, resource_id, *args, **kwargs):

        tus_file = TusFile.get_tusfile_or_404(str(resource_id))
        chunk = TusChunk(request)

        if not tus_file.is_valid():
            return TusResponse(status=410)

        if chunk.offset != tus_file.offset:
            return TusResponse(status=409)

        if chunk.offset > tus_file.file_size:
            return TusResponse(status=413)

        tus_file.write_chunk(chunk=chunk)

        if tus_file.is_complete():
            # file transfer complete, rename from resource id to actual filename
            tus_file.rename()
            tus_file.clean()

            self.send_signal(tus_file)
            self.finished()
            print("UPLOAD COMPLETED SUCCESSFULLY ")
            print("YOU CAN NOW CALL ANOTHER FUNCTION TO DO ANOTHER THING")
            filepath = tus_file.get_path()
            # create a thread
            # thread = Thread(target=unpack_json_upload, args=(filepath))
            # run the thread
            # thread.start()
            unpack_json_upload.delay(filepath)
        return TusResponse(status=204, extra_headers={"Upload-Offset": tus_file.offset})

    def send_signal(self, tus_file):
        tus_upload_finished_signal.send(
            sender=self.__class__,
            metadata=tus_file.metadata,
            filename=tus_file.filename,
            upload_file_path=tus_file.get_path(),
            file_size=tus_file.file_size,
            upload_url=settings.TUS_UPLOAD_URL,
            destination_folder=settings.TUS_DESTINATION_DIR,
        )

    def validate_filename(self, metadata):
        filename = metadata.get("filename", "")
        if not is_valid_filename(filename):
            filename = FilenameGenerator.random_string(16)
        return filename


# TODO complete this part of downloading files from the web
class FileDownloadListAPIView(generics.ListAPIView):
    def get(self, request, format=None):
        # queryset = Example.objects.get(id=id)
        # file_handle = queryset.file.path
        fileId = request.data["fileId"]
        userId = request.data["userId"]
        deviceId = request.data["deviceId"]
        filepath = pack(userId=userId, deviceId=deviceId, fileId=fileId)
        document = open(filepath, "rb")
        response = HttpResponse(  # change content_type = "text/txt"
            FileWrapper(document), content_type="application/msword"
        )
        response["Content-Disposition"] = 'attachment; filename="%s"' % filepath
        return response
