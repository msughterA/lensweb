from django.db import models

# Create your models here.
class Account(models.Model):
	username=models.CharField(max_length=20,null=True)
	phone_number=models.CharField(max_length=20)
	email=models.EmailField()
	password=models.CharField(max_length=8)
	device_id=models.CharField(blank=True,max_length=100)
	created_at=models.DateTimeField(null=True,auto_now_add=True)
	updated_at=models.DateTimeField(null=True,auto_now=True)
	# also include date when the account was created

	def __str__(self):
		return self.username



class Login(models.Model):
	phone_number=models.CharField(max_length=20)
	password=models.CharField(max_length=8)
	account_id=models.ForeignKey(Account,related_name='logs',on_delete=models.CASCADE)
	isActive=models.BooleanField(default=True)
	device_id=models.CharField(max_length=100)
	login_at=models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.phone_number	