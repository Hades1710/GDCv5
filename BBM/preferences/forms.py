from django import forms
from . import models

class PreferenceForm(forms.Form):
    student_backgrounds = forms.ModelMultipleChoiceField(
        queryset=models.StudentBackground.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    educational_interests = forms.ModelMultipleChoiceField(
        queryset=models.EducationalInterest.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    specific_needs = forms.ModelMultipleChoiceField(
        queryset=models.SpecificNeed.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    ) 