from django import forms
from django.contrib.auth.models import User
from . import models


class DonorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password','email']
        widgets = {
        'password': forms.PasswordInput(),
        'email': forms.EmailInput(attrs={'class': 'input--style-5'})
        }

class DonorForm(forms.ModelForm):
    class Meta:
        model=models.Donor
        fields=['max_donation_amount','address','mobile','profile_pic']

class DonationForm(forms.ModelForm):
    class Meta:
        model=models.BloodDonate
        fields=['age','bloodgroup','disease','unit']
