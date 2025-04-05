from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.core.mail import send_mail
from django.contrib.auth.models import User
from blood import forms as bforms
from blood import models as bmodels
from preferences import forms as pforms
from django.contrib import messages
from decimal import Decimal
import os
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from datetime import datetime
from patient.models import Patient
from bloodbankmanagement.location_utils import get_coordinates_from_address, find_nearby_students, calculate_distance

try:
    import firebase_admin
    from firebase_admin import credentials, auth
    
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate(r'C:\Users\7440\OneDrive\Desktop\BBM\BBM Erin update\BBM\serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    FIREBASE_ENABLED = True
except:
    FIREBASE_ENABLED = False
    print("Firebase Admin SDK not initialized. Email verification will not work.")

def donor_signup_view(request):
    userForm=forms.DonorUserForm()
    donorForm=forms.DonorForm()
    preferenceForm=pforms.PreferenceForm()
    mydict={'userForm':userForm,'donorForm':donorForm,'preferenceForm':preferenceForm}
    
    if request.method=='POST':
        userForm=forms.DonorUserForm(request.POST)
        donorForm=forms.DonorForm(request.POST,request.FILES)
        preferenceForm=pforms.PreferenceForm(request.POST)
        
        if userForm.is_valid() and donorForm.is_valid() and preferenceForm.is_valid():
            # Create Django user
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            
            donor=donorForm.save(commit=False)
            donor.user=user
            donor.save()
            
            # Save preferences
            donor.student_backgrounds.set(preferenceForm.cleaned_data['student_backgrounds'])
            donor.educational_interests.set(preferenceForm.cleaned_data['educational_interests'])
            donor.specific_needs.set(preferenceForm.cleaned_data['specific_needs'])
            
            my_donor_group = Group.objects.get_or_create(name='DONOR')
            my_donor_group[0].user_set.add(user)
            
            messages.success(request, 'Account created successfully! You can now login.')
            return HttpResponseRedirect('donorlogin')
            
    return render(request,'donor/donorsignup.html',context=mydict)

def donor_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if the user exists
        try:
            user = User.objects.get(username=username)
            
            # Authenticate with Django
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect('donor-dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
    
    form = AuthenticationForm()
    return render(request, 'donor/donorlogin.html', {'form': form})

def donor_dashboard_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    patient_requests = bmodels.BloodRequest.objects.all().filter(request_by_patient__isnull=False).order_by('-date')
    dict={
        'donor': donor,
        'patient_requests': patient_requests,
        'student_backgrounds': donor.student_backgrounds.all(),
        'educational_interests': donor.educational_interests.all(),
        'specific_needs': donor.specific_needs.all(),
    }
    return render(request,'donor/donor_dashboard.html',context=dict)


def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            donor= models.Donor.objects.get(user_id=request.user.id)
            blood_request.request_by_donor=donor
            blood_request.save()
            return HttpResponseRedirect('request-history')  
    return render(request,'donor/makerequest.html',{'request_form':request_form})

def request_history_view(request):
    donor= models.Donor.objects.get(user_id=request.user.id)
    requests=bmodels.BloodRequest.objects.all().filter(request_by_donor=donor)
    return render(request,'donor/request_history.html',{'requests':requests})

@login_required(login_url='donorlogin')
def donation_history_view(request):
    donor = models.Donor.objects.get(user_id=request.user.id)
    donations = models.Payment.objects.filter(donor=donor).order_by('-date')
    
    # Calculate statistics
    total_amount = donations.aggregate(Sum('amount'))['amount__sum'] or 0
    completed_donations = donations.filter(status='COMPLETED').count()
    pending_donations = donations.filter(status='PENDING').count()
    
    context = {
        'donations': donations,
        'total_amount': total_amount,
        'completed_donations': completed_donations,
        'pending_donations': pending_donations,
    }
    return render(request, 'donor/donation_history.html', context)

@login_required(login_url='donorlogin')
def make_payment_view(request, pk):
    try:
        blood_request = bmodels.BloodRequest.objects.get(id=pk)
        donor = models.Donor.objects.get(user=request.user.id)
        
        # Get the custom amount from query parameters
        custom_amount = request.GET.get('amount')
        if custom_amount:
            try:
                custom_amount = float(custom_amount)
                if custom_amount > donor.max_donation_amount:
                    messages.error(request, 'Amount exceeds your maximum donation limit.')
                    return redirect('donor-dashboard')
                if custom_amount <= 0:
                    messages.error(request, 'Please enter a valid amount.')
                    return redirect('donor-dashboard')
            except ValueError:
                messages.error(request, 'Invalid amount specified.')
                return redirect('donor-dashboard')
        else:
            custom_amount = blood_request.amount
            
        # Check if the donor has enough balance
        if donor.max_donation_amount < custom_amount:
            messages.error(request, 'Insufficient balance. Please add more funds to your account.')
            return redirect('donor-dashboard')
            
        return render(request, 'donor/payment.html', {
            'request': blood_request,
            'donor': donor,
            'custom_amount': custom_amount
        })
    except bmodels.BloodRequest.DoesNotExist:
        messages.error(request, 'Request not found.')
        return redirect('donor-dashboard')

@login_required(login_url='donorlogin')
def process_payment_view(request, pk):
    try:
        blood_request = bmodels.BloodRequest.objects.get(id=pk)
        donor = models.Donor.objects.get(user=request.user.id)
        
        # Get the amount from query parameters
        amount = request.GET.get('amount')
        if amount:
            try:
                amount = Decimal(amount)
                
                # Validate amount
                if amount <= 0:
                    messages.error(request, 'Please enter a valid amount.')
                    return redirect('donor-dashboard')
                
                if amount > donor.max_donation_amount:
                    messages.error(request, 'Amount exceeds your maximum donation limit.')
                    return redirect('donor-dashboard')
                
                if amount > blood_request.amount:
                    messages.error(request, 'Amount exceeds the requested amount.')
                    return redirect('donor-dashboard')
                
                # Process the payment
                # 1. Reduce donor's balance
                donor.max_donation_amount -= amount
                donor.save()
                
                # 2. Update request's donated amount
                blood_request.donated_amount += amount
                
                # 3. Update contributors count
                blood_request.contributors_count += 1
                
                blood_request.save()
                
                # Generate a transaction ID
                import uuid
                import datetime
                transaction_id = str(uuid.uuid4()).upper()[:8]
                timestamp = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p")
                
                # Show payment success page
                return render(request, 'donor/payment_success.html', {
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'request': blood_request,
                    'donor': donor,
                    'timestamp': timestamp
                })
            except ValueError:
                messages.error(request, 'Invalid amount specified.')
                return redirect('donor-dashboard')
        else:
            messages.error(request, 'No amount specified.')
            return redirect('donor-dashboard')
    except bmodels.BloodRequest.DoesNotExist:
        messages.error(request, 'Request not found.')
        return redirect('donor-dashboard')

@login_required(login_url='donorlogin')
def mentor_dashboard(request):
    donor = models.Donor.objects.get(user=request.user)
    mentor_slots = models.MentorAvailability.objects.filter(donor=donor, is_available=True)
    
    # Get booked sessions for this donor
    booked_sessions = models.MentorSessionBooking.objects.filter(
        mentor_slot__donor=donor
    ).order_by('mentor_slot__available_date', 'mentor_slot__available_time')
    
    return render(request, 'donor/mentor_dashboard.html', {
        'mentor_slots': mentor_slots,
        'booked_sessions': booked_sessions
    })

@login_required(login_url='donorlogin')
def add_mentor_slot(request):
    if request.method == 'POST':
        donor = models.Donor.objects.get(user=request.user)
        specialty = request.POST.get('specialty')
        description = request.POST.get('description')
        teaching_mode = request.POST.get('teaching_mode')
        available_date = request.POST.get('available_date')
        available_time = request.POST.get('available_time')

        # Validate date is not in the past
        selected_date = datetime.strptime(available_date, '%Y-%m-%d').date()
        if selected_date < timezone.now().date():
            messages.error(request, 'Cannot select a date in the past')
            return redirect('add_mentor_slot')

        # Create mentor slot with location fields if in-person
        mentor_slot = models.MentorAvailability(
            donor=donor,
            specialty=specialty,
            description=description,
            teaching_mode=teaching_mode,
            available_date=available_date,
            available_time=available_time
        )

        if teaching_mode == 'in_person':
            mentor_slot.location_name = request.POST.get('location_name')
            mentor_slot.address = request.POST.get('address')
            mentor_slot.city = request.POST.get('city')
            mentor_slot.state = request.POST.get('state')
            mentor_slot.pincode = request.POST.get('pincode')

        mentor_slot.save()
        messages.success(request, 'Mentoring slot added successfully!')
        return redirect('mentor_dashboard')

    return render(request, 'donor/add_mentor_slot.html')

@login_required(login_url='donorlogin')
def delete_mentor_slot(request, slot_id):
    donor = models.Donor.objects.get(user=request.user)
    try:
        slot = models.MentorAvailability.objects.get(id=slot_id, donor=donor)
        slot.delete()
        messages.success(request, 'Mentor slot deleted successfully')
    except models.MentorAvailability.DoesNotExist:
        messages.error(request, 'Mentor slot not found')
    return redirect('mentor_dashboard')

@login_required(login_url='donorlogin')
def confirm_mentor_session(request, booking_id):
    """View to confirm a pending mentor session"""
    donor = models.Donor.objects.get(user=request.user)
    
    try:
        # Ensure the booking belongs to this donor
        booking = models.MentorSessionBooking.objects.get(
            id=booking_id,
            mentor_slot__donor=donor,
            status='pending'
        )
        
        # Update the status to confirmed
        booking.status = 'confirmed'
        booking.save()
        
        messages.success(request, f'Session with {booking.patient.get_name} has been confirmed.')
    except models.MentorSessionBooking.DoesNotExist:
        messages.error(request, 'Booking not found or already processed.')
    
    return redirect('mentor_dashboard')


@login_required(login_url='donorlogin')
def complete_mentor_session(request, booking_id):
    """View to mark a mentor session as completed"""
    donor = models.Donor.objects.get(user=request.user)
    
    try:
        # Ensure the booking belongs to this donor
        booking = models.MentorSessionBooking.objects.get(
            id=booking_id,
            mentor_slot__donor=donor,
            status__in=['pending', 'confirmed']  # Can only complete pending or confirmed sessions
        )
        
        # Update the status to completed
        booking.status = 'completed'
        booking.save()
        
        messages.success(request, f'Session with {booking.patient.get_name} has been marked as completed.')
    except models.MentorSessionBooking.DoesNotExist:
        messages.error(request, 'Booking not found or cannot be completed.')
    
    return redirect('mentor_dashboard')


@login_required(login_url='donorlogin')
def cancel_mentor_session(request, booking_id):
    """View to cancel a mentor session"""
    donor = models.Donor.objects.get(user=request.user)
    
    try:
        # Ensure the booking belongs to this donor
        booking = models.MentorSessionBooking.objects.get(
            id=booking_id,
            mentor_slot__donor=donor,
            status__in=['pending', 'confirmed']  # Can only cancel pending or confirmed sessions
        )
        
        # Update the status to cancelled
        booking.status = 'cancelled'
        booking.save()
        
        # Make the slot available again
        mentor_slot = booking.mentor_slot
        mentor_slot.is_booked = False
        mentor_slot.save()
        
        messages.success(request, f'Session with {booking.patient.get_name} has been cancelled.')
    except models.MentorSessionBooking.DoesNotExist:
        messages.error(request, 'Booking not found or cannot be cancelled.')
    
    return redirect('mentor_dashboard')

@login_required(login_url='donorlogin')
def impact_tracker(request):
    """View to display the donor's impact through donations and mentoring"""
    donor = models.Donor.objects.get(user=request.user)
    
    # Get payment history
    payments = models.Payment.objects.filter(donor=donor, status='COMPLETED')
    total_amount_donated = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get mentoring sessions
    completed_sessions = models.MentorSessionBooking.objects.filter(
        mentor_slot__donor=donor,
        status='completed'
    ).count()
    
    upcoming_sessions = models.MentorSessionBooking.objects.filter(
        mentor_slot__donor=donor,
        status__in=['pending', 'confirmed']
    ).count()
    
    # Count unique patients helped through mentoring
    students_helped = models.MentorSessionBooking.objects.filter(
        mentor_slot__donor=donor,
        status='completed'
    ).values('patient').distinct().count()
    
    # Create timeline of activities
    timeline_items = []
    
    # Add payments to timeline
    for payment in payments.order_by('-date')[:5]:
        timeline_items.append({
            'date': payment.date,
            'type': 'payment',
            'icon': 'rupee-sign',
            'description': f'Donated ₹{payment.amount} to support education'
        })
    
    # Add completed mentoring sessions to timeline
    for session in models.MentorSessionBooking.objects.filter(
        mentor_slot__donor=donor,
        status='completed'
    ).order_by('-booking_date')[:5]:
        timeline_items.append({
            'date': session.booking_date,
            'type': 'mentoring',
            'icon': 'chalkboard-teacher',
            'description': f'Mentoring session with {session.patient.get_name}'
        })
    
    # Sort timeline items by date (newest first)
    timeline_items.sort(key=lambda x: x['date'], reverse=True)
    
    context = {
        'donor': donor,
        'total_amount_donated': total_amount_donated,
        'completed_sessions': completed_sessions,
        'upcoming_sessions': upcoming_sessions,
        'students_helped': students_helped,
        'timeline_items': timeline_items[:10]  # Show only the 10 most recent activities
    }
    
    return render(request, 'donor/impact_tracker.html', context)


@login_required(login_url='donorlogin')
def manage_mentor_location(request):
    """View for mentors to add or update their location"""
    donor = models.Donor.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = forms.MentorLocationForm(request.POST)
        if form.is_valid():
            # Get form data
            location_name = form.cleaned_data['location_name']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            pincode = form.cleaned_data['pincode']
            
            # Try to geocode the address
            coordinates = get_coordinates_from_address(address, city, state, pincode)
            
            if coordinates:
                latitude, longitude = coordinates
                
                # Create or update MentorAvailability with location data
                # We'll create a placeholder availability entry to store the location
                mentor_location, created = models.MentorAvailability.objects.get_or_create(
                    donor=donor,
                    is_available=False,
                    defaults={
                        'specialty': 'Location Only',
                        'description': 'Location placeholder',
                        'teaching_mode': 'in_person',
                        'available_date': timezone.now().date(),
                        'available_time': timezone.now().time(),
                    }
                )
                
                mentor_location.location_name = location_name
                mentor_location.address = address
                mentor_location.city = city
                mentor_location.state = state
                mentor_location.pincode = pincode
                mentor_location.latitude = latitude
                mentor_location.longitude = longitude
                mentor_location.save()
                
                messages.success(request, 'Your location has been updated successfully.')
                return redirect('nearby_students')
            else:
                messages.error(request, 'Unable to geocode your address. Please check and try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Try to get existing location data from any MentorAvailability
        try:
            mentor_location = models.MentorAvailability.objects.filter(
                donor=donor,
                latitude__isnull=False,
                longitude__isnull=False
            ).first()
            
            if mentor_location:
                form = forms.MentorLocationForm(instance=mentor_location)
            else:
                form = forms.MentorLocationForm()
        except:
            form = forms.MentorLocationForm()
    
    return render(request, 'donor/manage_mentor_location.html', {'form': form})


@login_required(login_url='donorlogin')
def nearby_students(request):
    """View for mentors to see nearby students"""
    donor = models.Donor.objects.get(user=request.user)
    
    # Try to get mentor's location
    mentor_location = models.MentorAvailability.objects.filter(
        donor=donor,
        latitude__isnull=False,
        longitude__isnull=False
    ).first()
    
    if not mentor_location or not mentor_location.latitude or not mentor_location.longitude:
        messages.warning(request, 'Please add your location first to view nearby students.')
        return redirect('manage_mentor_location')
    
    # Get nearby students
    nearby_student_data = find_nearby_students(mentor_location.latitude, mentor_location.longitude)
    
    # Add extra data for display
    for student, distance in nearby_student_data:
        # Format distance
        if distance < 1:
            student.formatted_distance = f"{int(distance * 1000)} meters"
        else:
            student.formatted_distance = f"{distance:.1f} km"
    
    context = {
        'mentor_location': mentor_location,
        'nearby_students': nearby_student_data,
    }
    
    return render(request, 'donor/nearby_students.html', context)


@login_required(login_url='donorlogin')
def schedule_visit(request, student_id):
    """View for mentors to schedule a visit to a student's location"""
    donor = models.Donor.objects.get(user=request.user)
    
    try:
        student = Patient.objects.get(id=student_id)
        
        if not student.latitude or not student.longitude or not student.location_name:
            messages.error(request, 'This student does not have location information available.')
            return redirect('nearby_students')
        
        if request.method == 'POST':
            form = forms.MentorVisitForm(request.POST)
            if form.is_valid():
                visit = form.save(commit=False)
                visit.mentor = donor
                visit.student = student
                visit.status = 'scheduled'
                visit.save()
                
                messages.success(request, f'Visit scheduled successfully. The student will be notified.')
                return redirect('mentor_visits')
        else:
            form = forms.MentorVisitForm()
        
        context = {
            'form': form,
            'student': student,
            'donor': donor,
        }
        
        return render(request, 'donor/schedule_visit.html', context)
        
    except Patient.DoesNotExist:
        messages.error(request, 'Student not found.')
        return redirect('nearby_students')


@login_required(login_url='donorlogin')
def mentor_visits(request):
    """View for mentors to see their scheduled visits"""
    donor = models.Donor.objects.get(user=request.user)
    
    # Get upcoming visits
    upcoming_visits = models.MentorVisit.objects.filter(
        mentor=donor,
        status__in=['scheduled', 'confirmed'],
        visit_date__gte=timezone.now().date()
    ).order_by('visit_date', 'visit_time')
    
    # Get past visits
    past_visits = models.MentorVisit.objects.filter(
        mentor=donor
    ).exclude(
        status__in=['scheduled', 'confirmed'],
        visit_date__gte=timezone.now().date()
    ).order_by('-visit_date', '-visit_time')
    
    context = {
        'upcoming_visits': upcoming_visits,
        'past_visits': past_visits,
        'donor': donor
    }
    
    return render(request, 'donor/mentor_visits.html', context)


@login_required(login_url='donorlogin')
def complete_visit(request, visit_id):
    """View for mentors to mark a visit as completed"""
    donor = models.Donor.objects.get(user=request.user)
    
    try:
        # Ensure the visit belongs to this donor
        visit = models.MentorVisit.objects.get(
            id=visit_id,
            mentor=donor,
            status__in=['scheduled', 'confirmed']  # Can only complete scheduled or confirmed visits
        )
        
        # Update the status to completed
        visit.status = 'completed'
        visit.save()
        
        messages.success(request, f'Visit to {visit.student.get_name} has been marked as completed.')
    except models.MentorVisit.DoesNotExist:
        messages.error(request, 'Visit not found or cannot be completed.')
    
    return redirect('mentor_visits')


@login_required(login_url='donorlogin')
def cancel_visit(request, visit_id):
    """View for mentors to cancel a visit"""
    donor = models.Donor.objects.get(user=request.user)
    
    try:
        # Ensure the visit belongs to this donor
        visit = models.MentorVisit.objects.get(
            id=visit_id,
            mentor=donor,
            status__in=['scheduled', 'confirmed']  # Can only cancel scheduled or confirmed visits
        )
        
        # Update the status to cancelled
        visit.status = 'cancelled'
        visit.save()
        
        messages.success(request, f'Visit to {visit.student.get_name} has been cancelled.')
    except models.MentorVisit.DoesNotExist:
        messages.error(request, 'Visit not found or cannot be cancelled.')
    
    return redirect('mentor_visits')
