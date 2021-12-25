from django.db import models
import datetime
from accounts.models import Account

# Create your models here.
# Payment model
class Payment(models.Model):
	transaction_device_id=models.CharField(max_length=20)
	transaction_id=models.CharField(max_length=200)
	amount_paid=models.DecimalField(max_digits=5,decimal_places=3)
	account_id=models.ForeignKey(Account,related_name='accid',on_delete=models.CASCADE)
	date_of_payment=models.DateTimeField(null=True,auto_now_add=True)
	expiry_date=models.DateTimeField(null=True)

# Pin model
class Pin(models.Model):
	pin_id=models.CharField(max_length=200)
	isTaken=models.BooleanField(default=False)
	#payment_id=models.ForeignKey(payment,on_delete=models.CASCADE)
	phone_number=models.CharField(max_length=20,null=True)
	transaction_id=models.CharField(max_length=200,null=True)
	created_at=models.DateTimeField(null=True,auto_now_add=True)
	expiry_date=models.DateTimeField(null=True)