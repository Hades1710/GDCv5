from django.db import models
from patient import models as pmodels
from donor import models as dmodels
class Stock(models.Model):
    bloodgroup=models.CharField(max_length=10)
    unit=models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.bloodgroup

class BloodRequest(models.Model):
    EDUCATIONAL_CHOICES = [
        ('stem', 'STEM (Science, Technology, Engineering, Mathematics)'),
        ('arts', 'Arts & Humanities (Literature, History, Philosophy, Visual Arts)'),
        ('business', 'Business & Entrepreneurship'),
        ('medical', 'Medical & Healthcare Studies'),
        ('vocational', 'Vocational & Skill-Based Education'),
        ('sports', 'Sports & Physical Education'),
        ('music', 'Music & Performing Arts'),
        ('digital', 'Digital Literacy & Coding'),
    ]

    EDUCATION_CHOICES = [
        ('primary', 'Primary Education (1-5)'),
        ('middle', 'Middle School (6-8)'),
        ('secondary', 'Secondary Education (9-10)'),
        ('higher_secondary', 'Higher Secondary (11-12)'),
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]

    SPECIFIC_NEEDS_CHOICES = [
        ('tuition', 'Tuition fees'),
        ('books', 'Books & learning materials'),
        ('online', 'Online courses & certifications'),
        ('transport', 'School transportation costs'),
        ('digital', 'Internet access & digital devices'),
        ('special', 'Special education support'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    request_by_patient=models.ForeignKey(pmodels.Patient,null=True,on_delete=models.CASCADE)
    request_by_donor=models.ForeignKey(dmodels.Donor,null=True,on_delete=models.CASCADE)
    patient_name=models.CharField(max_length=30)
    patient_age=models.PositiveIntegerField()
    gender=models.CharField(max_length=6, choices=GENDER_CHOICES, default='male')
    reason=models.CharField(max_length=500)
    education=models.CharField(max_length=20, choices=EDUCATION_CHOICES, null=True, blank=True)
    educational_interest=models.CharField(max_length=20, choices=EDUCATIONAL_CHOICES, null=True, blank=True)
    specific_needs=models.CharField(max_length=20, choices=SPECIFIC_NEEDS_CHOICES, null=True, blank=True)
    specially_abled=models.CharField(max_length=3, choices=[('yes', 'Yes'), ('no', 'No')], default='no')
    annual_income=models.PositiveIntegerField(null=True, blank=True)
    recipient_details=models.CharField(max_length=200, default="Not specified")
    amount=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    donated_amount=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    contributors_count=models.PositiveIntegerField(default=0)
    status=models.CharField(max_length=20,default="Pending")
    date=models.DateField(auto_now=True)
    def __str__(self):
        return self.patient_name

        