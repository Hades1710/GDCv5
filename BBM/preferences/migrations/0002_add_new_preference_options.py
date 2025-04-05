from django.db import migrations

def add_new_preference_options(apps, schema_editor):
    StudentBackground = apps.get_model('preferences', 'StudentBackground')
    EducationalInterest = apps.get_model('preferences', 'EducationalInterest')
    SpecificNeed = apps.get_model('preferences', 'SpecificNeed')

    # Add new Student Background options
    new_backgrounds = [
        'Students with disabilities (visual, hearing, mobility impairments)',
        'First-generation learners (first in family to receive formal education)',
        'Refugee or displaced students',
        'Students from rural or tribal areas',
        'Female students (to promote gender equality in education)',
        'Children affected by natural disasters or conflicts'
    ]
    for background in new_backgrounds:
        StudentBackground.objects.get_or_create(name=background)

    # Add new Educational Interest options
    new_interests = [
        'Business & Entrepreneurship',
        'Medical & Healthcare Studies',
        'Vocational & Skill-Based Education (Plumbing, Carpentry, Electrician, etc.)',
        'Sports & Physical Education',
        'Music & Performing Arts',
        'Digital Literacy & Coding'
    ]
    for interest in new_interests:
        EducationalInterest.objects.get_or_create(name=interest)

    # Add new Specific Need options
    new_needs = [
        'Online courses & certifications',
        'School transportation costs',
        'Internet access & digital devices (laptops, tablets, mobile data)',
        'Special education support (assistive devices, therapy, etc.)'
    ]
    for need in new_needs:
        SpecificNeed.objects.get_or_create(name=need)

class Migration(migrations.Migration):
    dependencies = [
        ('preferences', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_new_preference_options),
    ] 