from django.db import migrations, models
import django.db.models.deletion

def add_preference_options(apps, schema_editor):
    StudentBackground = apps.get_model('preferences', 'StudentBackground')
    EducationalInterest = apps.get_model('preferences', 'EducationalInterest')
    SpecificNeed = apps.get_model('preferences', 'SpecificNeed')

    # Add Student Background options
    StudentBackground.objects.create(name='Orphaned or abandoned children')
    StudentBackground.objects.create(name='Children from single-parent households')
    StudentBackground.objects.create(name='Students from low-income families')
    StudentBackground.objects.create(name='Students with disabilities (visual, hearing, mobility impairments)')
    StudentBackground.objects.create(name='First-generation learners (first in family to receive formal education)')
    StudentBackground.objects.create(name='Refugee or displaced students')
    StudentBackground.objects.create(name='Students from rural or tribal areas')
    StudentBackground.objects.create(name='Female students (to promote gender equality in education)')
    StudentBackground.objects.create(name='Children affected by natural disasters or conflicts')

    # Add Educational Interest options
    EducationalInterest.objects.create(name='STEM (Science, Technology, Engineering, Mathematics)')
    EducationalInterest.objects.create(name='Arts & Humanities (Literature, History, Philosophy, Visual Arts)')
    EducationalInterest.objects.create(name='Business & Entrepreneurship')
    EducationalInterest.objects.create(name='Medical & Healthcare Studies')
    EducationalInterest.objects.create(name='Vocational & Skill-Based Education (Plumbing, Carpentry, Electrician, etc.)')
    EducationalInterest.objects.create(name='Sports & Physical Education')
    EducationalInterest.objects.create(name='Music & Performing Arts')
    EducationalInterest.objects.create(name='Digital Literacy & Coding')

    # Add Specific Need options
    SpecificNeed.objects.create(name='Tuition fees')
    SpecificNeed.objects.create(name='Books & learning materials')
    SpecificNeed.objects.create(name='Online courses & certifications')
    SpecificNeed.objects.create(name='School transportation costs')
    SpecificNeed.objects.create(name='Internet access & digital devices (laptops, tablets, mobile data)')
    SpecificNeed.objects.create(name='Special education support (assistive devices, therapy, etc.)')

def remove_preference_options(apps, schema_editor):
    StudentBackground = apps.get_model('preferences', 'StudentBackground')
    EducationalInterest = apps.get_model('preferences', 'EducationalInterest')
    SpecificNeed = apps.get_model('preferences', 'SpecificNeed')

    StudentBackground.objects.all().delete()
    EducationalInterest.objects.all().delete()
    SpecificNeed.objects.all().delete()

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('donor', '0002_auto_20210213_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentBackground',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('donors', models.ManyToManyField(related_name='student_backgrounds', to='donor.Donor')),
            ],
        ),
        migrations.CreateModel(
            name='SpecificNeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('donors', models.ManyToManyField(related_name='specific_needs', to='donor.Donor')),
            ],
        ),
        migrations.CreateModel(
            name='EducationalInterest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('donors', models.ManyToManyField(related_name='educational_interests', to='donor.Donor')),
            ],
        ),
        migrations.RunPython(add_preference_options),
    ] 