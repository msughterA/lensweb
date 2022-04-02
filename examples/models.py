import pickle
from django.db import models
import base64
import json
import numpy as np

# Create your models here.

# question model
class Question(models.Model):
    text=models.TextField(max_length=4000)
    subject=models.TextField(max_length=20,null=True)
    embedding=models.TextField(max_length=12000)
    exam=models.TextField(max_length=10)
    year=models.CharField(max_length=6,null=True)
    answer=models.TextField(max_length=4000,blank=True,null=True)
    
   
# diagram model
class Diagram(models.Model):
    url=models.URLField()
    base64string=models.TextField(max_length=300)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)    
    