from django.db import models
from django.contrib.auth.models import User
from patient.models import Patient
from preferences.models import StudentBackground, EducationalInterest, SpecificNeed

EDUCATION_CHOICES = [
    ('PRIMARY', 'Primary School'),
    ('SECONDARY', 'Secondary School'),
    ('HIGHER_SECONDARY', 'Higher Secondary'),
    ('UNDERGRADUATE', 'Undergraduate'),
    ('GRADUATE', 'Graduate'),
]

EDUCATIONAL_INTEREST_CHOICES = [
    ('GENERAL', 'General Education'),
    ('STEM', 'Science & Technology'),
    ('ARTS', 'Arts & Humanities'),
    ('COMMERCE', 'Commerce & Business'),
    ('VOCATIONAL', 'Vocational Training'),
]

SPECIFIC_NEEDS_CHOICES = [
    ('NONE', 'None'),
    ('DISABILITY', 'Disability Support'),
    ('FINANCIAL', 'Financial Aid'),
    ('TRANSPORT', 'Transportation'),
    ('SUPPLIES', 'Educational Supplies'),
]

class Donor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Donor/', null=True, blank=True)
    max_donation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    bloodgroup = models.CharField(max_length=10, default="A+")
    disease = models.CharField(max_length=100, default="Nothing")
    age = models.CharField(max_length=3, default="30")
    unit = models.CharField(max_length=10, default="0")
    status = models.CharField(max_length=20, default="Pending")
    date = models.DateField(auto_now=True)
    
    # Add the many-to-many relationships
    student_backgrounds = models.ManyToManyField(StudentBackground, blank=True)
    educational_interests = models.ManyToManyField(EducationalInterest, blank=True)
    specific_needs = models.ManyToManyField(SpecificNeed, blank=True)
    
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.username

class BloodDonate(models.Model): 
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)   
    disease = models.CharField(max_length=100, default="Nothing")
    age = models.PositiveIntegerField()
    bloodgroup = models.CharField(max_length=10, default="A+")
    unit = models.PositiveIntegerField(default=1)
    date = models.DateField(auto_now=True)
    status = models.CharField(max_length=20, default="Pending")
    def __str__(self):
        return self.donor.user.username+" ["+self.status+"]"

class PatientRequest(models.Model):
    request_by_patient = models.ForeignKey(Patient, null=True, on_delete=models.CASCADE)
    patient_name = models.CharField(max_length=40)
    patient_age = models.PositiveIntegerField()
    reason = models.CharField(max_length=500)
    bloodgroup = models.CharField(max_length=10)
    unit = models.PositiveIntegerField(default=1)
    date = models.DateField(auto_now=True)
    status = models.CharField(max_length=30, default="Pending")
    education = models.CharField(max_length=20, choices=EDUCATION_CHOICES, default='PRIMARY')
    educational_interest = models.CharField(max_length=20, choices=EDUCATIONAL_INTEREST_CHOICES, default='GENERAL')
    specific_needs = models.CharField(max_length=20, choices=SPECIFIC_NEEDS_CHOICES, default='NONE')
    annual_income = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    donated_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    contributors_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.patient_name

class MentorAvailability(models.Model):
    SPECIALTY_CHOICES = [
        ('mathematics', 'Mathematics'),
        ('science', 'Science'),
        ('english', 'English'),
        ('computer_science', 'Computer Science'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('other', 'Other'),
    ]
    
    TEACHING_MODE_CHOICES = [
        ('online', 'Online'),
        ('in_person', 'In Person'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    specialty = models.CharField(max_length=100)
    description = models.TextField()
    teaching_mode = models.CharField(max_length=20, choices=TEACHING_MODE_CHOICES)
    available_date = models.DateField()
    available_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    
    # Location fields for in-person mentoring
    location_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.donor.get_name} - {self.specialty} ({self.available_date} {self.available_time})"

class MentorSessionBooking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    mentor_slot = models.ForeignKey(MentorAvailability, on_delete=models.CASCADE, related_name='bookings')
    patient = models.ForeignKey('patient.Patient', on_delete=models.CASCADE, related_name='mentor_bookings')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, help_text="Any specific topics or questions for the mentor")
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Patient's phone number for voice calls")
    meeting_link = models.URLField(blank=True, null=True, help_text="Video call meeting link")
    
    class Meta:
        ordering = ['-booking_date']
        
    def __str__(self):
        return f"Booking: {self.patient.user.username} with {self.mentor_slot.donor.user.username} on {self.mentor_slot.available_date}"

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    patient_request = models.ForeignKey('blood.BloodRequest', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default="Card")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment of ₹{self.amount} by {self.donor.user.username} on {self.date.strftime('%Y-%m-%d')}"

class MentorVisit(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    mentor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='visits')
    student = models.ForeignKey('patient.Patient', on_delete=models.CASCADE, related_name='mentor_visits')
    visit_date = models.DateField()
    visit_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    subject = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-visit_date', '-visit_time']
        
    def __str__(self):
        return f"Visit: {self.mentor.get_name} to {self.student.get_name} on {self.visit_date}"