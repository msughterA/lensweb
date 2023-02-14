import pickle
from django.db import models
import base64
import json
import numpy as np
from accounts.models import Account


# Create your models here.


# Collection Model
class Collection(models.Model):
    postedBy = models.ForeignKey(Account, on_delete=models.CASCADE)
    school = models.TextField()
    year = models.IntegerField()
    length = models.IntegerField()
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)


# question model
class Question(models.Model):
    text_map = models.TextField(blank=True, null=True)
    text_embedding = models.TextField(blank=True, null=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, blank=True, null=True
    )


# text model
class QuestionText(models.Model):
    question_text = models.TextField(blank=True, null=True)
    # text_embedding = models.TextField()
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, blank=True, null=True
    )


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, blank=True, null=True
    )
    answer_map = models.TextField(blank=True, null=True)
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, blank=True, null=True
    )


class AnswerText(models.Model):
    answer_text = models.TextField(blank=True, null=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)


# diagram model
class QuestionDiagram(models.Model):
    base64string = models.TextField(blank=True, null=True)
    # diagram_embedding = models.TextField()
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, blank=True, null=True
    )


class AnswerDiagram(models.Model):
    base64string = models.TextField(blank=True, null=True)
    # diagram_embedding = models.TextField()
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, blank=True, null=True)


# video or animation model
# class Video(models.Model):
#     pass
