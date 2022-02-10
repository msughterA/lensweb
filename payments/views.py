from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import datetime
import secrets
import string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from .models import Payment,Pin
from .serializers import PaymentSerializer,PinSerializer
from accounts.models import Account
import os
#test paystack api key
#skTest=os.environ['PAYSTACK_API_KEY']
skTest=''
# Authentication tokens
headers = {
   'Content-type': 'application/json',
   'Authorization': f'Bearer {skTest}'}

#paystack verification url
PAYSTACK_VERIFICATION_URL='https://api.paystack.co/transaction/verify/'

# initialize all the required parameters
paystack_secret_key = skTest
paystack = Paystack(secret_key=paystack_secret_key)

DURATION_OF_SUBSCRIPTION=30
DURATION_OF_FREE_TRIAL=7
def validate_transaction_id(transaction_id):
	# the payment id would be sent to paystack through their api to confirm if their transaction is valid
	response=Transaction.verify(transaction_id)
	#response_body=response.json()
	print(response)
	if response['status']==True:
		#verification success
		return True
	else:
		#verification failure
		print('This is the response status')
		print(response['status'])
		return False
# Function to generate free trial id
def generate_free_trial_id(phone_number):
	free_trial_id='free_trial'+'_'+phone_number+'_'+str(datetime.datetime.now())
	return free_trial_id
# Function to generate pin subscription id
def generate_pin_subscription_id(transaction_id):
	pin_subscription_id='pin_subscription'+'_'+transaction_id+'_'+str(datetime.datetime.now())
	return pin_subscription_id
# Calculate subscription expiry date
def calculate_expiring_date(now):
    #Get the current datetime
    end_date = now + datetime.timedelta(days=DURATION_OF_SUBSCRIPTION)
    return end_date
# Calculate free trial expiry date
def calculate_free_trial_expiring_date(now):
    end_date = now + datetime.timedelta(days=DURATION_OF_FREE_TRIAL)
    return end_date	
# Free trial subscription 
def free_trial_subscription(request_data):
	try:
			user=Account.objects.filter(phone_number__iexact=request_data['phone_number']).get()
			phone_number=request_data['phone_number']
	except Account.DoesNotExist:
		phone_number=request_data['phone_number']
		return Response({'message':f'account with number {phone_number} does not exist'})
	now = datetime.datetime.now()
	expiry_date=calculate_expiring_date(now)
	transaction_id=generate_free_trial_id(phone_number)	
	data={'transaction_device_id':request_data['transaction_device_id'],
			'transacation_id':transaction_id,
			'account_id':user.id,'amount_paid':request_data['amount_paid'],
			'expiry_date':expiry_date}
	serializer=PaymentSerializer(data)
	if serializer.is_valid(raise_exception=True):
		serializer.save()
		return Response({'message':f'you have gotten {DURATION_OF_FREE_TRIAL} subscription'},status=status.HTTP_201_CREATED)

def validate_subscription_expiry(id):
	payment_model=Payment.objects.get(id)
	now=datetime.datetime.now()
	if payment_model.expiry_date>now:
		return True
	else:
		return False
# method to generate subscription pin
def generate_subscription_pin():
	# The subsciption pin is actually an 11 digit number
	subscription_pin=secrets.choice(string.digits)
	subscription_pin+=secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	subscription_pin += secrets.choice(string.digits)
	return subscription_pin

# Create your views here.
# Payment view to handle payments with paystack api
class CardSubscriptionView(APIView):
	def get(self,request):
		payment_model=Payment.objects.all()
		serializer=PaymentSerializer(payment_model,many=True)
		return Response(serializer.data)
	def post(self,request):
            print(request.data)
            phone_number=request.data['phone_number']
            try:
                user=Account.objects.filter(phone_number__iexact=request.data['phone_number']).get()
                
            except Account.DoesNotExist:
                
                return Response({'message':f'account with number {phone_number} does not exist'})
            # uncomment this section of code when in live production	
            #if not validate_transaction_id(request.data['transaction_id']):
            #	return Response({'message':'Invalid transaction id'},status=status.HTTP_400_BAD_REQUEST)	
            now = datetime.datetime.now()
            expiry_date=calculate_expiring_date(now)	
            data={'transaction_device_id':request.data['transaction_device_id'],
                    'transaction_id':request.data['transaction_id'],
                    'account_id':user.id,'amount_paid':request.data['amount_paid'],
                    'expiry_date':expiry_date}
            serializer=PaymentSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message':'Payment successful'},status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response({'message':'Data Validation error'},status=status.HTTP_400_BAD_REQUEST)		

# Pin view to handle pin subscription
class PinSubscriptionView(APIView):
		
	def post(self,request):
		# validate user phone number
		# user is required to post phone_number,pin_id and amount_paid
		if request.data['phone_number'] and request.data['pin_id'] and request.data['amount_paid']:
			phone_number=request.data['phone_number']
			pin_id=request.data['pin_id']
			amount_paid=request.data['amount_paid']
		else:
			return Response({'message':'must provide phone_number, pin_id and amount_paid'})	
		try:
			user=Account.objects.filter(phone_number__iexact=request.data['phone_number']).get()
			phone_number=request.data['phone_number']
		except Account.DoesNotExist:
			phone_number=request.data['phone_number']
			return Response({'message':f'account with number {phone_number} does not exist'})	
		# check is pin exists in data base
		try:
			pin_model=Pin.objects.filter(pin_id__iexact=pin_id).get()
			# check if pin is taken
			if pin_model.isTaken==True:
				return Response({'message':'pin has already been taken'},status=status.HTTP_400_BAD_REQUEST)
			else:
				pin_model.isTaken=True	
		except Account.DoesNotExist:
			phone_number=request.data['pin_id']
			return Response({'message':f'pin does not exist'})
		now = datetime.datetime.now()
		expiry_date=calculate_expiring_date(now)		
		# generate pin subscription id
		subscription_id=generate_pin_subscription_id(pin_model.transaction_id)
		# data initialization
		data={'transaction_device_id':'online_device_id',
				'transaction_id':subscription_id,
				'account_id':user.id,'amount_paid':amount_paid,
				'expiry_date':expiry_date}
			
		# subscribe	
		serializer=PaymentSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response({'message':'Payment successful'},status=status.HTTP_201_CREATED)
		return Response({'message':'Data Validation error'},status=status.HTTP_400_BAD_REQUEST)	


# pin view to handle pin Generation and also show all the available pins i.e for people that want to sell the pin
class PinGenerationView(APIView):
	def get(self,request):
		pin_model=Pin.objects.all()
		serializer=PinSerializer(pin_model,many=True)
		return Response(serializer.data)
	def post(self,request):
		# user is required to post phone_number and paystack transaction_id
		# call the pin generator to get unique pin id
		if request.data['phone_number'] and request.data['transaction_id']:
			phone_number=request.data['phone_number']
			transaction_id=request.data['transaction_id']
		else:
			return Response({'message':'must provide phone_number and transaction_id'})	
		subscription_pin=generate_subscription_pin()
		try:
			pin=Account.objects.filter(phone_number__iexact=request.data['phone_number']).get()
		except Account.DoesNotExist:
			phone_number=request.data['phone_number']
			return Response({'message':f'account with number {phone_number} does not exist'})
		# uncomment this section of code in live production 	
		#if not validate_transaction_id(request.data['transaction_id']):
		#	return Response({'message':'Invalid transaction id'},status=status.HTTP_400_BAD_REQUEST)	
		now = datetime.datetime.now()
		expiry_date=calculate_expiring_date(now)
		data={'pin_id':subscription_pin,'expiry_date':expiry_date,'isTaken':False,'phone_number':phone_number,
				'transaction_id':transaction_id}
		serializer=PinSerializer(data=data)
		if serializer.is_valid(raise_exception=True):
			serializer.save()
			return Response({'pin':subscription_pin},status=status.HTTP_201_CREATED)
		return Response({'message':'Data Validation error'},status=status.HTTP_400_BAD_REQUEST)
