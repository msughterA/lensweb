from django.db import models

# Create your models here.
class Summarizer(models.Model):
    text=models.TextField(max_length=2000)
    summary=models.TextField(max_length=2000)
