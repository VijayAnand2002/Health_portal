import os
import django
import sys

# Add backend directory to sys.path to find health_portal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_portal.settings')
django.setup()

from accounts.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile

print("Fixing missing User Profiles...")
users_fixed = 0

for user in User.objects.all():
    if user.role == 'PATIENT':
        profile, created = PatientProfile.objects.get_or_create(user=user)
        if created:
            print(f"Created PatientProfile for {user.username}")
            users_fixed += 1
    elif user.role == 'DOCTOR':
        profile, created = DoctorProfile.objects.get_or_create(user=user)
        if created:
            print(f"Created DoctorProfile for {user.username}")
            users_fixed += 1

print(f"Done. Created {users_fixed} missing profiles.")
