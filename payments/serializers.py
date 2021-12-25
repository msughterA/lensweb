from .models import Payment,Pin
from accounts.serializers import AccountSerializer
from rest_framework import serializers

class PaymentSerializer(serializers.ModelSerializer):
	accid=AccountSerializer(read_only=True,many=True)
	class Meta:
		model=Payment
		fields='__all__'
	transaction_device_id=serializers.CharField(max_length=20)
	transaction_id=serializers.CharField(max_length=200)
	amount_paid=serializers.DecimalField(max_digits=5,decimal_places=3)
	#account_id=serializers.RelatedField(many=True,read_only=True)
	expiry_date=serializers.DateTimeField()	

	def create(self,validated_data):
		return Payment.objects.create(**validated_data)

	def update(self,instance,validated_data):
		instance.transaction_device_id=instance.get('transaction_device_id',instance.transaction_device_id)
		instance.transaction_id=instance.get('transaction_id',instance.transaction_id)
		instance.amount_paid=instance.get('amount_paid',instance.amount_paid)
		#instance.account_id=instance.get('account_id',instance.account_id)
		instance.expiry_date=instance.get('expiry_date',instance.expiry_date)
		instance.save()	
		return instance


class PinSerializer(serializers.ModelSerializer):
	class Meta:
		model=Pin
		fields='__all__'
	pin_id=serializers.CharField(max_length=200)
	#payment_id=serializers.IntegerField(max_length=20)
	isTaken=serializers.BooleanField()
	transaction_id=serializers.CharField(max_length=200)
	expiry_date=serializers.DateTimeField()	
	phone_number=serializers.CharField(max_length=20)
	def create(self,validated_data):
		return Pin.objects.create(**validated_data)

	def update(self,instance,validated_data):
		instance.pin_id=instance.get('pin_id',instance.pin_id)
		instance.isTaken=instance.get('isTaken',instance.isTaken)
		instance.expiry_date=instance.get('expiry_date',instance.expiry_date)
		instance.phone_number=instance.get('phone_number',instance.phone_number)
		instance.transaction_id=instance.get('transaction_id',instance.transaction_id)
		instance.save()
		return instance	
					