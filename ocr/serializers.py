from .models import *
from rest_framework import serializers



class OcrSerializer(serializers.ModelSerializer):
	class Meta:
		model=Ocr
		field='__all__'

