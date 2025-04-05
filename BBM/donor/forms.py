from django import forms
from django.contrib.auth.models import User
from . import models


class DonorUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password','email']
        widgets = {
        'password': forms.PasswordInput()
        }

class DonorForm(forms.ModelForm):
    class Meta:
        model=models.Donor
        fields=['max_donation_amount','address','mobile','profile_pic']

class DonationForm(forms.ModelForm):
    class Meta:
        model=models.BloodDonate
        fields=['age','bloodgroup','disease','unit']

class MentorAvailabilityForm(forms.ModelForm):
    class Meta:
        model=models.MentorAvailability
        fields=['specialty', 'description', 'teaching_mode', 'available_date', 'available_time', 
               'location_name', 'address', 'city', 'state', 'pincode']
        widgets = {
            'available_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'available_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'specialty': forms.Select(attrs={'class': 'form-control'}),
            'teaching_mode': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'location_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MentorLocationForm(forms.ModelForm):
    class Meta:
        model=models.MentorAvailability
        fields=['location_name', 'address', 'city', 'state', 'pincode']
        widgets = {
            'location_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MentorVisitForm(forms.ModelForm):
    class Meta:
        model=models.MentorVisit
        fields=['visit_date', 'visit_time', 'subject', 'notes']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
