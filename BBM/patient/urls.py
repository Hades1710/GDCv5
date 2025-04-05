from django.urls import path

from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('patientlogin', LoginView.as_view(template_name='patient/patientlogin.html'),name='patientlogin'),
    path('patientsignup', views.patient_signup_view,name='patientsignup'),
    path('patient-dashboard', views.patient_dashboard_view,name='patient-dashboard'),
    path('make-request', views.make_request_view,name='make-request'),
    path('my-request', views.my_request_view,name='my-request'),
    path('chatbot', views.chatbot_view, name='patient-chatbot'),
    path('api/gemini', views.gemini_api, name='gemini-api'),
    path('mentor-slots', views.mentor_slots_view, name='mentor-slots'),
    path('book-mentor-session/<int:slot_id>', views.book_mentor_session, name='book-mentor-session'),
    path('my-mentor-sessions', views.my_mentor_sessions, name='my-mentor-sessions'),
    path('cancel-mentor-booking/<int:booking_id>', views.cancel_mentor_booking, name='cancel-mentor-booking'),
    
    # Location-based features
    path('manage-location', views.manage_location_view, name='patient-manage-location'),
    path('my-mentor-visits', views.my_mentor_visits, name='my-mentor-visits'),
    path('confirm-mentor-visit/<int:visit_id>', views.confirm_mentor_visit, name='confirm-mentor-visit'),
]
