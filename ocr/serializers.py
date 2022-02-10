from .models import *
from rest_framework import serializers



class OcrSerializer(serializers.ModelSerializer):
	class Meta:
		model=Ocr
		fields='__all__'

