import os
import django
import sys

# Add backend directory to sys.path to find health_portal modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'health_portal.settings')
django.setup()

from accounts.models import User
from hospitals.models import Hospital
from doctors.models import DoctorProfile

def seed_hospitals():
    print("Seeding database...")
    
    # 1. Create a Hospital Admin User
    admin_username = 'city_hospital_admin'
    admin_email = 'admin@cityhospital.com'
    
    admin, created = User.objects.get_or_create(
        username=admin_username,
        defaults={
            'email': admin_email,
            'role': 'HOSPITAL_ADMIN',
            'is_approved': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"Created Hospital Admin: {admin_username}")
    else:
        print(f"Hospital Admin {admin_username} already exists")

    # 2. Create a Hospital
    hospital, created = Hospital.objects.get_or_create(
        registration_number='CH-2024-001',
        defaults={
            'name': 'City General Hospital',
            'email': 'contact@cityhospital.com',
            'phone': '011-23456789',
            'address_line1': '123 Medical Square',
            'city': 'New Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'description': 'A leading multi-specialty hospital providing advanced healthcare services.',
            'facilities': 'ICU, Emergency, Pharmacy, Radiology',
            'specializations': 'Cardiology, Neurology, Orthopedics, Pediatrics',
            'admin': admin,
            'is_verified': True
        }
    )
    if created:
        print(f"Created Hospital: {hospital.name}")
    else:
        print(f"Hospital {hospital.name} already exists")

    # 3. Create a Doctor and link to Hospital
    doctor_user, created = User.objects.get_or_create(
        username='dr_sharma',
        defaults={
            'first_name': 'Rakesh',
            'last_name': 'Sharma',
            'email': 'dr.sharma@example.com',
            'role': 'DOCTOR',
            'is_approved': True
        }
    )
    if created:
        doctor_user.set_password('doctor123')
        doctor_user.save()
        
        doctor_profile, _ = DoctorProfile.objects.get_or_create(
            user=doctor_user,
            defaults={
                'specialization': 'Cardiology',
                'license_number': 'MC-12345',
                'experience_years': 15,
                'is_available': True
            }
        )
        doctor_profile.hospitals.add(hospital)
        print(f"Created Doctor: Dr. {doctor_user.last_name} and linked to {hospital.name}")

    print("Seeding complete!")

if __name__ == "__main__":
    seed_hospitals()
