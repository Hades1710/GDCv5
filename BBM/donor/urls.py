from django.urls import path

from django.contrib.auth.views import LoginView
from . import views
urlpatterns = [
    path('donorlogin', LoginView.as_view(template_name='donor/donorlogin.html'),name='donorlogin'),
    path('donorsignup', views.donor_signup_view,name='donorsignup'),
    path('donor-dashboard', views.donor_dashboard_view,name='donor-dashboard'),
    path('donation-history', views.donation_history_view,name='donation-history'),
    path('make-request', views.make_request_view,name='make-request'),
    path('request-history', views.request_history_view,name='request-history'),
    path('make-payment/<int:pk>', views.make_payment_view,name='make-payment'),
    path('process-payment/<int:pk>', views.process_payment_view,name='process-payment'),
    path('mentor-dashboard', views.mentor_dashboard, name='mentor_dashboard'),
    path('add-mentor-slot', views.add_mentor_slot, name='add_mentor_slot'),
    path('delete-mentor-slot/<int:slot_id>', views.delete_mentor_slot, name='delete_mentor_slot'),
    path('confirm-mentor-session/<int:booking_id>', views.confirm_mentor_session, name='confirm_mentor_session'),
    path('complete-mentor-session/<int:booking_id>', views.complete_mentor_session, name='complete_mentor_session'),
    path('cancel-mentor-session/<int:booking_id>', views.cancel_mentor_session, name='cancel_mentor_session'),
    path('impact-tracker', views.impact_tracker, name='impact_tracker'),
    
    # Location-based features
    path('manage-location', views.manage_mentor_location, name='manage_mentor_location'),
    path('nearby-students', views.nearby_students, name='nearby_students'),
    path('schedule-visit/<int:student_id>', views.schedule_visit, name='schedule_visit'),
    path('mentor-visits', views.mentor_visits, name='mentor_visits'),
    path('complete-visit/<int:visit_id>', views.complete_visit, name='complete_visit'),
    path('cancel-visit/<int:visit_id>', views.cancel_visit, name='cancel_visit'),
]