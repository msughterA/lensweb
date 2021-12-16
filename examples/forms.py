from django import forms

class AdminLogInForm(forms.Form):
    email=forms.CharField(max_length=40,
    widget=forms.TextInput(attrs={'class':'input100','type':'text',
                                  'name':'email','placeholder':'email'}))
    password=forms.CharField(max_length=8,
    widget=forms.TextInput(attrs={'class':'input100','type':'password',
                                  'name':'pass','placeholder':'password'}))
    
    
    
class UploadFileForm(forms.Form):     
     file=forms.FileField()