from django.db import models
from accounts.models import Account

# Create your models here.
class FileSend(models.Model):
    user = models.ForeignKey(Account, related_name="send", on_delete=models.CASCADE)
    # the number of byte chunks in the file
    chunkCount = models.IntegerField()
    # the index of the last chunk sent
    pointer = models.IntegerField()


class FileReceive(models.Model):
    user = models.ForeignKey(Account, related_name="receive", on_delete=models.CASCADE)
    # the number of byte chunks in the file
    chunkCount = models.IntegerField()
    # the index of the last chunk sent
    pointer = models.IntegerField()
