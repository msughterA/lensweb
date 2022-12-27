from django.contrib import admin
from .models import FileReceive, FileSend

# Register your models here.
admin.site.register(FileSend)
admin.site.register(FileReceive)
