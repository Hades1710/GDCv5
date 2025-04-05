from django.db import models
from django.contrib.auth.models import User

class Patient(models.Model):
    BACKGROUND_CHOICES = [
        ('orphaned', 'Orphaned or abandoned children'),
        ('single_parent', 'Children from single-parent households'),
        ('low_income', 'Students from low-income families'),
        ('disabilities', 'Students with disabilities'),
        ('first_gen', 'First-generation learners'),
        ('refugee', 'Refugee or displaced students'),
        ('rural_tribal', 'Students from rural or tribal areas'),
        ('female', 'Female students'),
        ('disaster', 'Affected by natural disasters or conflicts'),
    ]

    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Patient/',null=True,blank=True)

    age=models.PositiveIntegerField()
    bloodgroup=models.CharField(max_length=10)
    disease=models.CharField(max_length=100)
    doctorname=models.CharField(max_length=50)

    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    introduction = models.TextField(max_length=500, blank=True, null=True)
    education = models.CharField(max_length=100, blank=True, null=True)
    annual_income = models.PositiveIntegerField(blank=True, null=True)
    student_background = models.CharField(max_length=20, choices=BACKGROUND_CHOICES, null=True, blank=True)
    # Location fields
    location_name = models.CharField(max_length=255, blank=True, null=True, help_text="Name of the location")
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name