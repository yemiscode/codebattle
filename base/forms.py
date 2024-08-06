from django.forms import ModelForm
from .models import  Submission, User
from django.contrib.auth.forms import UserCreationForm


class UserForm(ModelForm):
    class Meta: 
        model = User
        fields = ['username','email', 'avatar', 'bio']

class SubmissionForm(ModelForm):
    class Meta:
        model = Submission
        fields = ['details']
   
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','name', 'password1', 'password2']  