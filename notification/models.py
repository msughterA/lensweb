from django.db import models
from accounts.models import Account


# Create your models here.
class NotificationModel(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    message = models.CharField(max_length=3000)
