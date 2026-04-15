from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from hospitals.models import Hospital
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from appointments.models import Appointment
import datetime

User = get_user_model()

class HospitalActionTests(TestCase):
    def setUp(self):
        # Create Hospital Admin
        self.admin_user = User.objects.create_user(
            username='hosp_admin', 
            email='admin@hosp.com', 
            password='password', 
            role='HOSPITAL_ADMIN'
        )
        
        # Create Hospital
        self.hospital = Hospital.objects.create(
            name='Test Hospital',
            admin=self.admin_user,
            city='Test City',
            state='Test State'
        )
        
        # Create Doctor and affiliate with hospital
        self.doctor_user = User.objects.create_user(
            username='doctor', 
            email='doctor@example.com', 
            password='password', 
            role='DOCTOR'
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user, 
            license_number='DOC001', 
            specialization='General'
        )
        self.hospital.doctors.add(self.doctor_profile)
        
        # Create Patient
        self.patient_user = User.objects.create_user(
            username='patient', 
            email='patient@example.com', 
            password='password', 
            role='PATIENT'
        )
        self.patient_profile = PatientProfile.objects.create(user=self.patient_user)
        
        # Create Appointment
        self.appointment = Appointment.objects.create(
            doctor=self.doctor_profile,
            patient=self.patient_profile,
            appointment_date=datetime.date.today(),
            consultation_fee=500,
            status='PENDING'
        )
        self.client = Client()

    def test_hospital_admin_approves_appointment(self):
        self.client.login(username='hosp_admin', password='password')
        url = reverse('hospitals:approve_appointment', args=[self.appointment.id])
        # Need to provide appointment_time in POST data
        response = self.client.post(url, {'appointment_time': '11:00'})
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'CONFIRMED')
        self.assertEqual(str(self.appointment.appointment_time), '11:00:00')
        # Check if redirected back or to dashboard (HTTP_REFERER defaults to DASHBOARD in view)
        self.assertEqual(response.status_code, 302)

    def test_hospital_admin_rejects_appointment(self):
        self.client.login(username='hosp_admin', password='password')
        url = reverse('hospitals:reject_appointment', args=[self.appointment.id])
        response = self.client.post(url)
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'CANCELLED')
        self.assertEqual(response.status_code, 302)
