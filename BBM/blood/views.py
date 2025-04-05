from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from decimal import Decimal
from django.db import models as django_models

def home_view(request):
    x=models.Stock.objects.all()
    print(x)
    if len(x)==0:
        blood1=models.Stock()
        blood1.bloodgroup="A+"
        blood1.save()

        blood2=models.Stock()
        blood2.bloodgroup="A-"
        blood2.save()

        blood3=models.Stock()
        blood3.bloodgroup="B+"
        blood3.save()        

        blood4=models.Stock()
        blood4.bloodgroup="B-"
        blood4.save()

        blood5=models.Stock()
        blood5.bloodgroup="AB+"
        blood5.save()

        blood6=models.Stock()
        blood6.bloodgroup="AB-"
        blood6.save()

        blood7=models.Stock()
        blood7.bloodgroup="O+"
        blood7.save()

        blood8=models.Stock()
        blood8.bloodgroup="O-"
        blood8.save()

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')  
    return render(request,'blood/index.html')

def is_donor(user):
    return user.groups.filter(name='DONOR').exists()

def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin-dashboard')
        elif hasattr(request.user, 'donor'):
            return redirect('donor-dashboard')
        elif hasattr(request.user, 'patient'):
            return redirect('patient-dashboard')
    return redirect('home')

@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    # Get counts and data for the admin dashboard
    donors = dmodels.Donor.objects.all()
    patients = pmodels.Patient.objects.all()
    blooddonate = dmodels.BloodDonate.objects.all()
    requests = models.BloodRequest.objects.all()
    
    context = {
        'donors': donors,
        'patients': patients,
        'blooddonate': blooddonate,
        'requests': requests,
    }
    return render(request, 'blood/admin_dashboard.html', context)

@login_required(login_url='adminlogin')
def admin_blood_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    blooddonate = dmodels.BloodDonate.objects.all()
    return render(request, 'blood/admin_blood.html', {'blooddonate': blooddonate})


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donors = dmodels.Donor.objects.all()
    return render(request, 'blood/admin_donor.html', {'donors': donors})

@login_required(login_url='adminlogin')
def update_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=dmodels.User.objects.get(id=donor.user_id)
    userForm=dforms.DonorUserForm(instance=user)
    donorForm=dforms.DonorForm(request.FILES,instance=donor)
    mydict={'userForm':userForm,'donorForm':donorForm}
    if request.method=='POST':
        userForm=dforms.DonorUserForm(request.POST,instance=user)
        donorForm=dforms.DonorForm(request.POST,request.FILES,instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.bloodgroup=donorForm.cleaned_data['bloodgroup']
            donor.save()
            return redirect('admin-donor')
    return render(request,'blood/update_donor.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request,pk):
    donor=dmodels.Donor.objects.get(id=pk)
    user=User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    return HttpResponseRedirect('/admin-donor')

@login_required(login_url='adminlogin')
def admin_patient_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patients = pmodels.Patient.objects.all()
    return render(request, 'blood/admin_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
def update_patient_view(request,pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient = pmodels.Patient.objects.get(id=pk)
    user = pmodels.User.objects.get(id=patient.user_id)
    userForm = pforms.PatientUserForm(instance=user)
    patientForm = pforms.PatientForm(request.FILES,instance=patient)
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=pforms.PatientUserForm(request.POST,instance=user)
        patientForm=pforms.PatientForm(request.POST,request.FILES,instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.bloodgroup=patientForm.cleaned_data['bloodgroup']
            patient.save()
            return redirect('admin-patient')
    return render(request,'blood/update_patient.html',context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request,pk):
    patient=pmodels.Patient.objects.get(id=pk)
    user=User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return HttpResponseRedirect('/admin-patient')

@login_required(login_url='adminlogin')
def admin_request_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    requests = models.BloodRequest.objects.filter(status='Pending')
    return render(request, 'blood/admin_request.html', {'requests': requests})

@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    requests = models.BloodRequest.objects.exclude(status='Pending')
    return render(request, 'blood/admin_request_history.html', {'requests': requests})

@login_required(login_url='adminlogin')
def admin_donation_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donations = dmodels.BloodDonate.objects.all()
    return render(request, 'blood/admin_donation.html', {'donations': donations})

@login_required(login_url='adminlogin')
def update_approve_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    message=None
    bloodgroup=req.bloodgroup
    unit=req.unit
    stock=models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit > unit:
        stock.unit=stock.unit-unit
        stock.save()
        req.status="Approved"
        
    else:
        message="Stock Doest Not Have Enough Blood To Approve This Request, Only "+str(stock.unit)+" Unit Available"
    req.save()

    requests=models.BloodRequest.objects.all().filter(status='Pending')
    return render(request,'blood/admin_request.html',{'requests':requests,'message':message})

@login_required(login_url='adminlogin')
def update_reject_status_view(request,pk):
    req=models.BloodRequest.objects.get(id=pk)
    req.status="Rejected"
    req.save()
    return HttpResponseRedirect('/admin-request')

@login_required(login_url='adminlogin')
def approve_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation_blood_group=donation.bloodgroup
    donation_blood_unit=donation.unit

    stock=models.Stock.objects.get(bloodgroup=donation_blood_group)
    stock.unit=stock.unit+donation_blood_unit
    stock.save()

    donation.status='Approved'
    donation.save()
    return HttpResponseRedirect('/admin-donation')


@login_required(login_url='adminlogin')
def reject_donation_view(request,pk):
    donation=dmodels.BloodDonate.objects.get(id=pk)
    donation.status='Rejected'
    donation.save()
    return HttpResponseRedirect('/admin-donation')

def home(request):
    # Get statistics for the home page
    total_donors = dmodels.Donor.objects.count()
    
    # Calculate total donations amount
    total_donations = models.BloodRequest.objects.filter(status='Approved').aggregate(Sum('donated_amount'))['donated_amount__sum']
    if total_donations is None:
        total_donations = 0
    
    # Calculate total beneficiaries (patients who received donations)
    total_beneficiaries = models.BloodRequest.objects.filter(status='Approved').count()
    
    context = {
        'total_donors': total_donors,
        'total_donations': total_donations,
        'total_beneficiaries': total_beneficiaries,
    }
    
    return render(request, 'home.html', context)

def how_it_works(request):
    return render(request, 'how_it_works.html')

def impact(request):
    # Get statistics for the impact page
    total_donors = dmodels.Donor.objects.count()
    
    # Calculate total donations amount
    payments = dmodels.Payment.objects.filter(status='COMPLETED')
    total_donations = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Count total beneficiaries (patients)
    total_beneficiaries = pmodels.Patient.objects.count()
    
    # Count total mentoring sessions
    total_mentoring_sessions = dmodels.MentorSessionBooking.objects.filter(status='completed').count()
    
    context = {
        'total_donors': total_donors,
        'total_donations': total_donations,
        'total_beneficiaries': total_beneficiaries,
        'total_mentoring_sessions': total_mentoring_sessions,
    }
    
    return render(request, 'impact.html', context)

def adminlogin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin-dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'blood/adminlogin.html')

def logout_view(request):
    logout(request)
    return redirect('home')