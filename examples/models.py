from django.db import models

# Create your models here.

# question model
class Question(models.Model):
    text=models.TextField(max_length=500)
    embedding=models.TextField(max_length=2000)
    exam=models.TextField(max_length=10)
    year=models.CharField(max_length=6,null=True)
    answer=models.TextField(max_length=2000,blank=True,null=True)
    

# diagram model
class Diagram(models.Model):
    url=models.URLField()
    base64string=models.TextField(max_length=300)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)    
