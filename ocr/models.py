from django.db import models

# Create your models here.

# Ocr model
class Ocr(models.Model):
    base64string=models.TextField(max_length=3000)
    text=models.TextField(max_length=1000)
    created_at=models.DateTimeField(auto_now_add=True)