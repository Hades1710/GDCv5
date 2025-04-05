from django import forms
from django.contrib.auth.models import User
from . import models


class PatientUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets = {
        'password': forms.PasswordInput()
        }

class PatientForm(forms.ModelForm):
    
    class Meta:
        model=models.Patient
        fields=['address','mobile','profile_pic','introduction','education','annual_income','location_name','latitude','longitude']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class PatientLocationForm(forms.ModelForm):
    class Meta:
        model=models.Patient
        fields=['location_name','address']
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location name (e.g. Home, School)'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complete address'}),
        }
