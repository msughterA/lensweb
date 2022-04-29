import email
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account,Login
from .serializers import AccountSerializer,LoginSerializer


# Create your views here.

#Method for data validation
def validate_password_strength(password):
	# if password is weak return the appropriate error
	if len(password)!=8:
         return Response(status=status.HTTP_400_BAD_REQUEST)
def validate_duplicate_data(username,email,phone_number):
	# if username, email, phone_number is already in the database return the appropriate error
	validate_duplicate_username(username)
	#validate duplicate phone number
	validate_duplicate_phone_number(phone_number)
	#validate duplicate email
	validate_duplicate_email(email)
def validate_duplicate_username(username):	
	# if not accountDB.objects.filter(username__iexact=username)
	#if username in accountDB.objects.all().username:
	if Account.objects.filter(username__iexact=username):
		print("username taken")
		return True
def validate_duplicate_phone_number(phone_number):		
	if Account.objects.filter(phone_number__iexact=phone_number):
		return True
def validate_duplicate_email(email):		
	if Account.objects.filter(email__iexact=email):
	    return True	
def run_validations(username,email,phone_number,password):
    # check if the details are not empty
    #validate_details_isNot_empty(username,email,phone_number,password)
    #validate the strength of the password
    validate_password_strength(password)
    #validate if username, email,phone number already exists in the database
    validate_duplicate_data(username,email,phone_number)



# check if the strength of password is okay	
# Method for writing data to account Database i.e account creation
class VerifyDataView(APIView):
    def post(self,request):
            serializer=AccountSerializer(data=request.data)
            #validate data format
            if serializer.is_valid(raise_exception=True):
                # run validations
                data=serializer.validated_data
                print('Data is valid')
                #run_validations(data['username'],data['email'],data['phone_number'],data['password'])
                if validate_duplicate_username(data['username']):
                    return Response({'message':'username already taken'},status=status.HTTP_401_UNAUTHORIZED)
                elif validate_duplicate_phone_number(data['phone_number']):
                    return Response({'message':'phone number already taken'},status=status.HTTP_401_UNAUTHORIZED)
                elif validate_duplicate_email(data['email']):
                    return Response({'message':'email already taken'},status=status.HTTP_401_UNAUTHORIZED)		
                return Response({'message':'Details are valid'},status=status.HTTP_200_OK  )
            print('Data is not valid')    
            #return Response({'message':'Bad request'},status=status.HTTP_400_BAD_REQUEST)
        
class AccountView(APIView):
	
    def get(self,request):
        account=Account.objects.all()
        serializer=AccountSerializer(account,many=True)
        return Response(serializer.data)
    def post(self,request):
            serializer=AccountSerializer(data=request.data)
            #validate data format
            print('request recorded')
            if serializer.is_valid():
                # run validations
                print('Account creation data is valid')
                data=serializer.validated_data
                #run_validations(data['username'],data['email'],data['phone_number'],data['password'])
                if validate_duplicate_username(data['username']):
                    return Response({'message':'username already taken'},status=status.HTTP_401_UNAUTHORIZED)
                elif validate_duplicate_phone_number(data['phone_number']):
                    return Response({'message':'phone number already taken'},status=status.HTTP_401_UNAUTHORIZED)
                elif validate_duplicate_email(data['email']):
                    return Response({'message':'email already taken'},status=status.HTTP_401_UNAUTHORIZED)
                
                serializer.save()
                user=Account.objects.filter(phone_number__iexact=data['phone_number']).get()
                login_data={'phone_number':data['phone_number'],'device_id':data['device_id'],'account_id':user.id,
				'password':data['password'],'isActive':True}		
                if validate_phone_number_and_password(data['phone_number'],data['password']):
                    loginSerializer=LoginSerializer(data=login_data)
                    if loginSerializer.is_valid(raise_exception=True):
                        loginSerializer.save()
                        return Response({'message':'Login successful'})
                    return Response({'message':'you must provide details in valid format'})
                return Response({'message':'account creted successfuly'},status=status.HTTP_201_CREATED)
            print(serializer.errors)    
            return Response({'message':serializer.errors},status=status.HTTP_400_BAD_REQUEST)

    def put(self,request):
        # to update you need an existing object
        # use phone phone number to get
        data=request.data
        print(data)
        if 'phone_number' in data:
            phone_number=data['phone_number']
        else:
            print('you must provide a phone number')
            return Response({'message':'you must provide a phone_number'},status=status.HTTP_400_BAD_REQUEST)	
        
        try:
            user=Account.objects.filter(phone_number__iexact=phone_number).get()
            #serializer=accountDBSerializer(user,data=request.da)
            if 'email' in request.data:
                email=request.data['email']
                if validate_duplicate_email(email):
                    return Response({'message':'email already taken'},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    serializer=AccountSerializer(user,data={'email':email},partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()	
            elif 'username' in request.data:
                username=request.data['username']
                if validate_duplicate_username(username):
                    return Response({'message':'username is already taken'},status=status.HTTP_401_UNAUTHORIZED)
                else:
                    serializer=AccountSerializer(user,data={'username':username},partial=True)
                    if serializer.is_valid(): 
                        serializer.save()
            elif 'password' in request.data:
                password=request.data['password']
                if validate_password_strength(password):
                    return Response({"message":"password strength is weak"},status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer=AccountSerializer(user,data={'password':password},partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()
            elif 'new_phone_number' in request.data:
                new_phone_number=request.data['new_phone_number']
                if validate_duplicate_phone_number(new_phone_number):
                    return Response({'message':'phone number already taken'},status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer=AccountSerializer(user,data={'phone_number':new_phone_number},partial=True)
                    if serializer.is_valid(raise_exception=True):
                        serializer.save()					
            else:
                print('Nothing to update error')
                return Response({"message":"Nothing to update"},status=status.HTTP_400_BAD_REQUEST)
        except Account.DoesNotExist:
            return Response({'message':'phone number does not exist'},status=status.HTTP_400_BAD_REQUEST)	
        return Response({'message':'user account updated'},status=status.HTTP_201_CREATED)	
        #serializer=accountDBSerializer(request.data)
    def delete(self,request):
        data=request.data
        if 'phone_number' in data:
            phone_number=data['phone_number']
        else:
            return Response({'message':'you must provide a phone_number'},status=status.HTTP_400_BAD_REQUEST)
        try:
            user=Account.objects.filter(phone_number__iexact=phone_number).get()
            user.delete()
            return Response({'message':'user deleted'},status=status.HTTP_204_NO_CONTENT)
        except Account.DoesNotExist:
            return Response({'message':'phone_number does no exist'},status=status.HTTP_404_NOT_FOUND)		


# Function to validate phone number and password
def validate_phone_number_and_password(phone_number,password):
	try:
		user=Account.objects.filter(phone_number__iexact=phone_number).get()
		if user.password==password:
			return True
		else:
			return False
	except:
		return False			

class LoginView(APIView):
	def get(self,request):
		login_model=Login.objects.all()
		serializer=LoginSerializer(login_model,many=True)
		return Response(serializer.data)

	def post(self,request):
		if request.data['phone_number'] and request.data['password'] and request.data['device_id']:
			phone_number=request.data['phone_number']
			password=request.data['password']
			device_id=request.data['device_id']
		else:
			return Response({'message':'you must provide a phone_number and password'})
		try:
			user=Account.objects.filter(phone_number__iexact=phone_number).get()
			account_id=user.id
		except Account.DoesNotExist:
			return Response({'message':'invalid phone number or password'},status=status.HTTP_401_UNAUTHORIZED)		
		data={'phone_number':phone_number,'device_id':device_id,'account_id':account_id,
				'password':password,'isActive':True}		
		if validate_phone_number_and_password(phone_number,password):
			serializer=LoginSerializer(data=data)
			if serializer.is_valid(raise_exception=True):
				serializer.save()
                # Return the detail to be stored on the physical device
				return Response({'username':user.username,'phoneNumber':phone_number,'email':user.email,})
			return Response({'message':'you must provide details in valid format'})
		return Response({'message':'invalid phone number or password'},status=status.HTTP_400_BAD_REQUEST)
	# the delete should be called when user wants to log out
	# this method simply deletes the user from the login database	
	def delete(self,request):
		# The user is required to post phone_number and device id in order to logout
		if request.data['phone_number'] and request.data['device_id']:
			phone_number=request.data['phone_number']
			device_id=request.data['device_id']
		else:
			return Response({'message':'you must provide a phone_number and device_id'},status=status.HTTP_400_BAD_REQUEST)
		try:
			login_model=Login.objects.filter(device_id__iexact=device_id).get()
			login_model.delete()
			return Response({'message':'log out successful'})
		except Login.DoesNotExist:
			return Response({'message':'unable to logout please provide valid details'},status=status.HTTP_404_NOT_FOUND)		

