from django.db import models
from django.db.models.fields import EmailField

# Create your models here.
class AdminUser(models.Model):
    email=models.EmailField(max_length=25)
    password=models.CharField(max_length=8)
