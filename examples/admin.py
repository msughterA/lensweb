from django.contrib import admin
from .models import Question, QuestionDiagram, AnswerDiagram, Collection, QuestionText

# Register your models here.
admin.site.register(Question)
admin.site.register(QuestionDiagram)
admin.site.register(Collection)
admin.site.register(QuestionText)
