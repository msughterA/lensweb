from django.shortcuts import redirect, render
from .forms import AdminLogInForm, UploadFileForm
from django.views.decorators.http import require_POST
import json
# Create your views here.
def index(request):
    adminLogInForm=AdminLogInForm()
    context={'adminLogInForm':adminLogInForm}
    return render(request,'examples/index.html',context)

@require_POST
def login(request):
    adminLogInForm=AdminLogInForm(request.POST)
    context={}
    # if  the credentials are valid
    if adminLogInForm.is_valid():
        email=request.POST['email']
        password=request.POST['password']
    # Render the adminView
    # Display an Error on the form
    return render(request,'examples/uploadfile.html',context)


@require_POST
def upload(request):
    form = UploadFileForm(request.POST, request.FILES)
    context={'form':form}
    if form.is_valid():
       file= request.FILES['file']
       json_file=json.load(file)
      # print(json_file[0])
       if '.txt' not in file.name:
            redirect('uploadfile.html')
        
    return render(request,'examples/uploadfile.html')   