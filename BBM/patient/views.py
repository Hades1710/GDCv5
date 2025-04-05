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
import json
import os
import requests
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import logging
from donor.models import MentorAvailability, MentorSessionBooking, MentorVisit
from django.contrib import messages
from django.utils import timezone
from bloodbankmanagement.location_utils import get_coordinates_from_address, find_nearby_students

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Gemini API
API_KEY = "AIzaSyBrIxTCoWBjMtfAIfNFYH75UD7dYKlIMfo"
genai.configure(api_key=API_KEY)

def patient_signup_view(request):
    userForm=forms.PatientUserForm()
    patientForm=forms.PatientForm()
    mydict={'userForm':userForm,'patientForm':patientForm}
    if request.method=='POST':
        userForm=forms.PatientUserForm(request.POST)
        patientForm=forms.PatientForm(request.POST,request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            patient=patientForm.save(commit=False)
            patient.user=user
            patient.save()
            my_patient_group = Group.objects.get_or_create(name='PATIENT')
            my_patient_group[0].user_set.add(user)
        return HttpResponseRedirect('patientlogin')
    return render(request,'patient/patientsignup.html',context=mydict)

def patient_dashboard_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    dict={
        'requestpending': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Pending').count(),
        'requestapproved': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Approved').count(),
        'requestmade': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).count(),
        'requestrejected': bmodels.BloodRequest.objects.all().filter(request_by_patient=patient).filter(status='Rejected').count(),
        'patient': patient,
    }
   
    return render(request,'patient/patient_dashboard.html',context=dict)

def make_request_view(request):
    request_form=bforms.RequestForm()
    if request.method=='POST':
        request_form=bforms.RequestForm(request.POST)
        if request_form.is_valid():
            blood_request=request_form.save(commit=False)
            patient= models.Patient.objects.get(user_id=request.user.id)
            blood_request.request_by_patient=patient
            blood_request.save()
            return HttpResponseRedirect('my-request')  
    return render(request,'patient/makerequest.html',{'request_form':request_form})

def my_request_view(request):
    patient= models.Patient.objects.get(user_id=request.user.id)
    blood_request=bmodels.BloodRequest.objects.all().filter(request_by_patient=patient)
    return render(request,'patient/my_request.html',{'blood_request':blood_request})

@login_required(login_url='patientlogin')
def chatbot_view(request):
    return render(request, 'patient/chatbot.html')

@csrf_exempt
@login_required(login_url='patientlogin')
def gemini_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            chat_type = data.get('chatType', 'learning')  # Default to learning if not specified
            
            logger.info(f"Received {chat_type} request: {user_message[:50]}...")
            
            # First try with the Python client library
            try:
                response_text = generate_with_genai_library(user_message, chat_type)
                if response_text:
                    return JsonResponse({'response': response_text})
            except Exception as e:
                logger.error(f"Python client library failed: {str(e)}")
                logger.info("Trying direct API call as fallback...")
            
            # If that fails, try with direct API call
            try:
                response_text = generate_with_direct_api(user_message, chat_type)
                if response_text:
                    return JsonResponse({'response': response_text})
            except Exception as e:
                logger.error(f"Direct API call failed: {str(e)}")
            
            # If all automated methods fail, use our simulated responses
            logger.warning("All API methods failed, using simulated response")
            ai_response = get_simulated_response(user_message, chat_type)
            return JsonResponse({'response': ai_response})
            
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}", exc_info=True)
            # Fallback to simulated response
            ai_response = get_simulated_response(user_message, chat_type)
            return JsonResponse({'response': ai_response})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def generate_with_genai_library(user_message, chat_type):
    """Generate response using the Python client library"""
    # Set appropriate prompt based on chat type
    if chat_type == 'learning':
        prompt = f"Question: {user_message}\n\nProvide a helpful, educational response."
    else:  # emergency
        prompt = f"Emergency situation: {user_message}\n\nProvide immediate, practical guidance with steps to take."
    
    # Create model with safety settings
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    
    model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config
    )
    
    # Generate response
    response = model.generate_content(prompt)
    
    if response and hasattr(response, 'text') and response.text:
        return response.text
    return None

def generate_with_direct_api(user_message, chat_type):
    """Generate response using direct API call"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"
    
    # Set appropriate prompt based on chat type
    if chat_type == 'learning':
        prompt = f"Question: {user_message}\n\nProvide a helpful, educational response."
    else:  # emergency
        prompt = f"Emergency situation: {user_message}\n\nProvide immediate, practical guidance with steps to take."
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1024,
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        response_json = response.json()
        try:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        except (KeyError, IndexError):
            return None
    return None

def get_simulated_response(user_message, chat_type):
    """Generate a simulated response based on keywords in the user's message and chat type."""
    user_message = user_message.lower()
    
    if chat_type == 'learning':
        if any(word in user_message for word in ['photosynthesis', 'plant', 'oxygen']):
            return "Photosynthesis is the process by which green plants convert sunlight into energy. The plants use chlorophyll (the green pigment), water, carbon dioxide, and sunlight to produce glucose, oxygen, and water. The simplified equation is: 6CO₂ + 6H₂O + Light Energy → C₆H₁₂O₆ + 6O₂."
        
        elif any(word in user_message for word in ['math', 'equation', 'algebra', 'solve']):
            return "To solve algebraic equations, you need to isolate the variable. Here's a general approach:\n1. Simplify both sides of the equation\n2. Move all variable terms to one side\n3. Move all constant terms to the other side\n4. Divide both sides by the coefficient of the variable\nFor example, to solve 3x + 5 = 11:\n3x + 5 - 5 = 11 - 5\n3x = 6\nx = 6 ÷ 3\nx = 2"
        
        elif any(word in user_message for word in ['translate', 'hindi', 'english']):
            return "Here's the translation from English to Hindi:\n\n'Hello, how are you?' → 'नमस्ते, आप कैसे हैं?' (Namaste, aap kaise hain?)\n\nIf you'd like me to translate something specific, please provide the text."
        
        elif any(word in user_message for word in ['science', 'physics', 'chemistry', 'biology']):
            return "Science is divided into several branches: Physics studies matter, energy and their interactions; Chemistry examines substances and their properties; Biology explores living organisms. Which specific scientific concept would you like me to explain?"
        
        elif any(word in user_message for word in ['history', 'civilization', 'world war']):
            return "History helps us understand the past and how it shapes our present. It covers the rise and fall of civilizations, important events like World Wars, and cultural developments. What specific historical topic would you like to learn about?"
        
        else:
            return "I'm your Learning Assistant. I can help explain academic concepts, solve problems, or assist with translating text. Please let me know what specific topic you'd like to learn about."
    
    else:  # Emergency help
        if any(word in user_message for word in ['drop out', 'dropping', 'quit school']):
            return "I'm sorry to hear you're considering dropping out. This is a serious situation. Before making any decisions:\n\n1. Speak with a school counselor about your challenges\n2. Contact our foundation's emergency education hotline at [HOTLINE NUMBER]\n3. Check if you qualify for our emergency education grant\n4. Consider alternative education paths like flexible scheduling or online options\n\nWould you like me to help you connect with a student support coordinator who can provide personalized assistance?"
        
        elif any(word in user_message for word in ['fee', 'payment', 'due', 'tuition']):
            return "Regarding your urgent fee situation:\n\n1. Immediately contact your school's financial aid office to explain your situation\n2. Apply for our Emergency Education Fund through the 'Make Request' option in your dashboard - mark it as URGENT\n3. Ask about payment plan options at your institution\n4. Check if you qualify for any scholarships or hardship grants\n\nWould you like help preparing your emergency funding request?"
        
        elif any(word in user_message for word in ['access', 'internet', 'computer', 'books', 'resources', 'net']):
            return "For your resource access emergency:\n\n1. Our foundation provides emergency resource kits that include essential textbooks\n2. We can arrange temporary internet access cards for critical coursework\n3. Check your local library for computer access and extended hours\n4. We partner with several online education platforms that offer offline access options\n\nPlease use the 'Make Request' form to specify exactly what resources you need, and we'll prioritize your case."
        
        elif any(word in user_message for word in ['bully', 'discrimination', 'harass', 'unsafe']):
            return "I'm very sorry you're experiencing this. Your safety and wellbeing are top priorities:\n\n1. Document all incidents with dates, times, and details\n2. Report the situation to a trusted teacher or school administrator\n3. Contact our Student Protection Hotline at [HOTLINE NUMBER] for immediate guidance\n4. If you feel in danger, please contact local authorities\n\nWould you like me to help connect you with our student advocacy team?"
        
        else:
            return "I understand you're facing an educational emergency. To provide the best help, could you share more details about your specific situation? I'm here to help with urgent issues like financial emergencies, resource access problems, or situations that might force you to drop out. The more information you provide, the better guidance I can offer."

@login_required(login_url='patientlogin')
def mentor_slots_view(request):
    """View to display available mentor slots for patients"""
    # Get current date
    current_date = timezone.now().date()
    
    # Get all available mentor slots that are in the future
    available_slots = MentorAvailability.objects.filter(
        is_available=True,
        is_booked=False,
        available_date__gte=current_date
    ).order_by('available_date', 'available_time')
    
    # Group slots by specialty for easier display
    specialty_groups = {}
    for slot in available_slots:
        specialty = slot.specialty  # Changed from get_specialty_display()
        if specialty not in specialty_groups:
            specialty_groups[specialty] = []
        specialty_groups[specialty].append(slot)
    
    context = {
        'specialty_groups': specialty_groups,
        'total_slots': available_slots.count(),
    }
    
    return render(request, 'patient/mentor_slots.html', context)

@login_required(login_url='patientlogin')
def book_mentor_session(request, slot_id):
    """View to book a mentor session"""
    try:
        # Get the mentor slot
        mentor_slot = MentorAvailability.objects.get(id=slot_id, is_available=True, is_booked=False)
        
        # Get the patient
        patient = models.Patient.objects.get(user=request.user)
        
        if request.method == 'POST':
            notes = request.POST.get('notes', '')
            phone_number = None
            meeting_link = None
            
            # Handle teaching mode specific requirements
            if mentor_slot.teaching_mode == 'voice_call':
                phone_number = request.POST.get('phone_number', '')
                if not phone_number:
                    messages.error(request, 'Phone number is required for voice call sessions')
                    return render(request, 'patient/book_mentor_session.html', {'mentor_slot': mentor_slot})
            
            elif mentor_slot.teaching_mode == 'video_call':
                # Generate a Google Meet link
                # Format: https://meet.google.com/ + random 10-character string
                import random
                import string
                random_code = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
                meeting_link = f"https://meet.google.com/{random_code}"
            
            # Create the booking
            booking = MentorSessionBooking.objects.create(
                mentor_slot=mentor_slot,
                patient=patient,
                notes=notes,
                phone_number=phone_number,
                meeting_link=meeting_link
            )
            
            # Mark the slot as booked
            mentor_slot.is_booked = True
            mentor_slot.save()
            
            messages.success(request, 'Mentor session booked successfully!')
            return redirect('my-mentor-sessions')

        return render(request, 'patient/book_mentor_session.html', {'mentor_slot': mentor_slot})
    
    except MentorAvailability.DoesNotExist:
        messages.error(request, 'This mentor slot is no longer available.')
        return redirect('mentor-slots')

@login_required(login_url='patientlogin')
def my_mentor_sessions(request):
    """View to display a patient's booked mentor sessions"""
    patient = models.Patient.objects.get(user=request.user)
    current_date = timezone.now().date()
    
    # Get upcoming sessions (pending or confirmed, and date is in the future)
    upcoming_sessions = MentorSessionBooking.objects.filter(
        patient=patient,
        status__in=['pending', 'confirmed'],
        mentor_slot__available_date__gte=current_date
    ).order_by('mentor_slot__available_date', 'mentor_slot__available_time')
    
    # Get completed or cancelled sessions
    completed_cancelled = MentorSessionBooking.objects.filter(
        patient=patient,
        status__in=['completed', 'cancelled']
    )
    
    # Get sessions with past dates
    past_date_sessions = MentorSessionBooking.objects.filter(
        patient=patient,
        mentor_slot__available_date__lt=current_date
    )
    
    # Combine the two querysets for past sessions
    past_sessions = (completed_cancelled | past_date_sessions).distinct().order_by(
        '-mentor_slot__available_date', 'mentor_slot__available_time'
    )
    
    context = {
        'upcoming_sessions': upcoming_sessions,
        'past_sessions': past_sessions,
    }
    
    return render(request, 'patient/my_mentor_sessions.html', context)

@login_required(login_url='patientlogin')
def cancel_mentor_booking(request, booking_id):
    """View for patients to cancel their booked mentor sessions"""
    patient = models.Patient.objects.get(user=request.user)
    
    try:
        # Ensure the booking belongs to this patient
        booking = MentorSessionBooking.objects.get(
            id=booking_id,
            patient=patient,
            status__in=['pending', 'confirmed']  # Can only cancel pending or confirmed sessions
        )
        
        # Update the status to cancelled
        booking.status = 'cancelled'
        booking.save()
        
        # Make the slot available again
        mentor_slot = booking.mentor_slot
        mentor_slot.is_booked = False
        mentor_slot.save()
        
        messages.success(request, 'Your mentor session has been cancelled successfully.')
    except MentorSessionBooking.DoesNotExist:
        messages.error(request, 'Booking not found or cannot be cancelled.')
    
    return redirect('my-mentor-sessions')


@login_required(login_url='patientlogin')
def manage_location_view(request):
    """View for patients to add or update their location"""
    patient = models.Patient.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = forms.PatientLocationForm(request.POST, instance=patient)
        if form.is_valid():
            # Get form data
            location_name = form.cleaned_data['location_name']
            address = form.cleaned_data['address']
            
            # Get city, state, pincode from the patient's existing data
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            pincode = request.POST.get('pincode', '')
            
            # Try to geocode the address
            coordinates = get_coordinates_from_address(address, city, state, pincode)
            
            if coordinates:
                latitude, longitude = coordinates
                patient.latitude = latitude
                patient.longitude = longitude
                patient.location_name = location_name
                patient.save()
                messages.success(request, 'Your location has been updated successfully.')
                return redirect('patient-dashboard')
            else:
                messages.error(request, 'Unable to geocode your address. Please check and try again.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = forms.PatientLocationForm(instance=patient)
    
    return render(request, 'patient/manage_location.html', {'form': form, 'patient': patient})


@login_required(login_url='patientlogin')
def my_mentor_visits(request):
    """View for patients to see their scheduled in-person mentor visits"""
    patient = models.Patient.objects.get(user=request.user)
    
    # Get upcoming visits
    upcoming_visits = MentorVisit.objects.filter(
        student=patient,
        status__in=['scheduled', 'confirmed'],
        visit_date__gte=timezone.now().date()
    ).order_by('visit_date', 'visit_time')
    
    # Get past visits
    past_visits = MentorVisit.objects.filter(
        student=patient
    ).exclude(
        status__in=['scheduled', 'confirmed'],
        visit_date__gte=timezone.now().date()
    ).order_by('-visit_date', '-visit_time')
    
    context = {
        'upcoming_visits': upcoming_visits,
        'past_visits': past_visits,
        'patient': patient
    }
    
    return render(request, 'patient/my_mentor_visits.html', context)


@login_required(login_url='patientlogin')
def confirm_mentor_visit(request, visit_id):
    """View for patients to confirm a mentor visit"""
    patient = models.Patient.objects.get(user=request.user)
    
    try:
        # Ensure the visit is for this patient
        visit = MentorVisit.objects.get(
            id=visit_id,
            student=patient,
            status='scheduled'
        )
        
        # Update the status to confirmed
        visit.status = 'confirmed'
        visit.save()
        
        messages.success(request, 'You have confirmed the mentor visit successfully.')
    except MentorVisit.DoesNotExist:
        messages.error(request, 'Visit not found or cannot be confirmed.')
    
    return redirect('my-mentor-visits')
