from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from appointments.models import Appointment
import datetime

User = get_user_model()

class AppointmentApprovalTests(TestCase):
    def setUp(self):
        self.doctor_user = User.objects.create_user(username='doctor', email='doctor@example.com', password='password', role='DOCTOR')
        self.doctor_user.is_approved = True
        self.doctor_user.save()
        self.doctor_profile = DoctorProfile.objects.create(user=self.doctor_user, license_number='DOC001', specialization='General')
        
        self.patient_user = User.objects.create_user(username='patient', email='patient@example.com', password='password', role='PATIENT')
        self.patient_profile = PatientProfile.objects.create(user=self.patient_user)
        
        self.appointment = Appointment.objects.create(
            doctor=self.doctor_profile,
            patient=self.patient_profile,
            appointment_date=datetime.date.today(),
            consultation_fee=500,
            status='PENDING'
        )
        self.client = Client()

    def test_doctor_approves_with_time(self):
        self.client.login(username='doctor', password='password')
        url = reverse('doctors:approve_appointment', args=[self.appointment.id])
        response = self.client.post(url, {'appointment_time': '10:30'})
        
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'CONFIRMED')
        self.assertEqual(str(self.appointment.appointment_time), '10:30:00')
        self.assertRedirects(response, reverse('doctors:dashboard'))
