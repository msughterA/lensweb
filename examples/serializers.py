from .models import Question, Diagram
from rest_framework import serializers
import base64
import requests
import biology


def get_as_base64(url):
    """Function that takes url  of image, downloads it and converts it to base64

    Args:
        url (string): url path of image

    Returns:
        string: base64 string of the image
    """
    print(f"Getting image at {url}")
    return base64.b64encode(requests.get(url).content)


# Diagram Serializer
class DiagramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagram
        fields = ["url"]


# Question Serializer
class QuestionSerializer(serializers.ModelSerializer):
    diagrams = DiagramSerializer(many=True)

    class Meta:
        model = Question
        fields = ["text", "subject", "embedding", "exam", "year", "answer", "diagrams"]

    # create a question
    def create(self, validated_data):
        diagrams_data = validated_data.pop("diagrams")
        base64_diagrams = []
        [base64_diagrams.append(get_as_base64(dig["url"])) for dig in diagrams_data]
        question = Question.objects.create(**validated_data)
        # Diagram.objects.bulk_create(base64_diagrams)
        # diagram_objects=[]
        # diagram_object={}
        for dig, dig_url in zip(base64_diagrams, diagrams_data):
            # Diagram.objects.create(question=question,base64string=dig,url=dig_url['url'])
            # diagram_objects['question']=question
            # diagram_objects['base64string']=dig
            # diagram_objects['url']=dig_url['url']
            Diagram.objects.create(
                question=question, base64string=dig, url=dig_url["url"]
            )
        return question
