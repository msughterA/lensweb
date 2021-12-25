from django.db import models

# Create your models here.

# Ocr model
class Ocr(models.Model):
    base64string=models.TextField(max_length=300)
    text=models.TextField(max_length=300)
    created_at=models.DateTimeField(auto_now_add=True)