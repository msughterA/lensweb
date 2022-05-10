from .models import Account,Login
from rest_framework import serializers


'''
class accountDBSerializer(serializers.ModelSerializer):

   class Meta:
       model=accountDB
       fields='__all__'
'''

class AccountSerializer(serializers.ModelSerializer):
      class Meta:
          model=Account
          fields='__all__'
      username=serializers.CharField(max_length=20)
      phone_number=serializers.CharField(max_length=20)
      email=serializers.EmailField()
      password=serializers.CharField(max_length=20)
      device_id=serializers.CharField(max_length=100)
      #date=serializers.DateTimeField()      

      def create(self,validated_data):
         return Account.objects.create(**validated_data) 

      def update(self,instance,validated_data):
          instance.username=validated_data.get('username',instance.username)
          instance.phone_number=validated_data.get('phone_number',instance.phone_number)
          instance.email=validated_data.get('email',instance.email)
          instance.password=validated_data.get('password',instance.password)
          instance.save()
          return instance   



class LoginSerializer(serializers.ModelSerializer):
    logs=AccountSerializer(read_only=True,many=True)
    class Meta:
        model=Login
        fields='__all__'
    phone_number=serializers.CharField(max_length=20)
    password=serializers.CharField(max_length=20)
    isActive=serializers.BooleanField()
    device_id=serializers.CharField(max_length=100)

    def create(self,validated_data):
        return Login.objects.create(**validated_data)

    def update(self,instance,validated_data):
        instance.phone_number=validated_data.get('phone_number',instance.phone_number)
        instance.password=validated_data.get('password',instance.password)
        instance.device_id=validated_data.get('device_id',instance.device_id)
        instance.isActive=validated_data.get('isActive',instance.isActive)
        instance.save()
        return instance    
                     