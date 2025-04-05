from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from donor import models as dmodels
from patient import models as pmodels
from decimal import Decimal
from django.db import models

def home(request):
    # Get statistics for the home page
    total_donors = dmodels.Donor.objects.count()
    total_donations = dmodels.PatientRequest.objects.aggregate(total=models.Sum('donated_amount'))['total'] or Decimal('0')
    total_beneficiaries = pmodels.Patient.objects.count()
    
    context = {
        'total_donors': total_donors,
        'total_donations': total_donations,
        'total_beneficiaries': total_beneficiaries,
    }
    return render(request, 'home.html', context)

def afterlogin_view(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin-dashboard')
        elif hasattr(request.user, 'donor'):
            return redirect('donor-dashboard')
        elif hasattr(request.user, 'patient'):
            return redirect('patient-dashboard')
    return redirect('home')

def adminlogin_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin-dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'adminlogin.html')

def admin_dashboard_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donors = dmodels.Donor.objects.all()
    patients = pmodels.Patient.objects.all()
    blooddonate = dmodels.BloodDonate.objects.all()
    
    context = {
        'donors': donors,
        'patients': patients,
        'blooddonate': blooddonate,
    }
    return render(request, 'admin/admin_dashboard.html', context)

def admin_blood_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    blooddonate = dmodels.BloodDonate.objects.all()
    return render(request, 'admin/admin_blood.html', {'blooddonate': blooddonate})

def admin_donor_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donors = dmodels.Donor.objects.all()
    return render(request, 'admin/admin_donor.html', {'donors': donors})

def admin_patient_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patients = pmodels.Patient.objects.all()
    return render(request, 'admin/admin_patient.html', {'patients': patients})

def admin_request_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient_requests = pmodels.PatientRequest.objects.all()
    return render(request, 'admin/admin_request.html', {'patient_requests': patient_requests})

def admin_donation_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donations = dmodels.BloodDonate.objects.all()
    return render(request, 'admin/admin_donation.html', {'donations': donations})

def admin_request_history_view(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient_requests = pmodels.PatientRequest.objects.all()
    return render(request, 'admin/admin_request_history.html', {'patient_requests': patient_requests})

def update_approve_status_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient_request = pmodels.PatientRequest.objects.get(id=pk)
    patient_request.status = 'Approved'
    patient_request.save()
    return redirect('admin-request')

def update_reject_status_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient_request = pmodels.PatientRequest.objects.get(id=pk)
    patient_request.status = 'Rejected'
    patient_request.save()
    return redirect('admin-request')

def approve_donation_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    blooddonate = dmodels.BloodDonate.objects.get(id=pk)
    blooddonate.status = 'Approved'
    blooddonate.save()
    return redirect('admin-donation')

def reject_donation_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    blooddonate = dmodels.BloodDonate.objects.get(id=pk)
    blooddonate.status = 'Rejected'
    blooddonate.save()
    return redirect('admin-donation')

def update_donor_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donor = dmodels.Donor.objects.get(id=pk)
    if request.method == 'POST':
        donor.user.first_name = request.POST.get('first_name')
        donor.user.last_name = request.POST.get('last_name')
        donor.user.email = request.POST.get('email')
        donor.user.save()
        donor.address = request.POST.get('address')
        donor.mobile = request.POST.get('mobile')
        donor.save()
        return redirect('admin-donor')
    return render(request, 'admin/update_donor.html', {'donor': donor})

def delete_donor_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    donor = dmodels.Donor.objects.get(id=pk)
    donor.user.delete()
    return redirect('admin-donor')

def update_patient_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient = pmodels.Patient.objects.get(id=pk)
    if request.method == 'POST':
        patient.user.first_name = request.POST.get('first_name')
        patient.user.last_name = request.POST.get('last_name')
        patient.user.email = request.POST.get('email')
        patient.user.save()
        patient.address = request.POST.get('address')
        patient.mobile = request.POST.get('mobile')
        patient.save()
        return redirect('admin-patient')
    return render(request, 'admin/update_patient.html', {'patient': patient})

def delete_patient_view(request, pk):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return redirect('adminlogin')
    
    patient = pmodels.Patient.objects.get(id=pk)
    patient.user.delete()
    return redirect('admin-patient') 