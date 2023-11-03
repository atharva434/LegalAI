
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Client, Lawyer
from django.contrib.auth.models import User


class UserInfo(forms.ModelForm):
    password = forms.CharField(widget = forms.PasswordInput()) #hash out the password
    
    class Meta():
        model = User
        fields = ('username','password')
class ClientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'name', 'phno', 'state', 'Pincode']

class LawyerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Lawyer
        fields = ['email', 'name', 'lawyertype', 'phno', 'Pincode', 'enrollmentno', 'enrollmentstate', 'upi_id']
