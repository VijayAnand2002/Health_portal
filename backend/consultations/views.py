from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from appointments.models import Appointment
from .models import Consultation
import uuid
from django.contrib import messages

@login_required
def start_consultation_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if user is authorized (doctor only can start, patient can join)
    if request.user != appointment.doctor.user:
        messages.error(request, "Only the assigned doctor can start the consultation.")
        return redirect('accounts:dashboard')
    
    # Create or get consultation record
    consultation, created = Consultation.objects.get_or_create(
        appointment=appointment,
        defaults={'room_id': f"room_{uuid.uuid4().hex[:10]}"}
    )
    
    if created:
        consultation.status = 'ACTIVE'
        consultation.save()
        
    return redirect('consultations:room', room_id=consultation.room_id)

@login_required
def join_consultation_view(request, room_id):
    consultation = get_object_or_404(Consultation, room_id=room_id)
    appointment = consultation.appointment
    
    # Check if user is part of this appointment
    if request.user != appointment.patient.user and request.user != appointment.doctor.user:
        messages.error(request, "Access denied. You are not a participant in this consultation.")
        return redirect('accounts:dashboard')
    
    context = {
        'consultation': consultation,
        'appointment': appointment,
        'is_doctor': request.user == appointment.doctor.user,
    }
    return render(request, 'consultations/room.html', context)

@login_required
def end_consultation_view(request, room_id):
    consultation = get_object_or_404(Consultation, room_id=room_id)
    
    if request.user == consultation.appointment.doctor.user:
        consultation.status = 'COMPLETED'
        consultation.save()
        consultation.appointment.status = 'COMPLETED'
        consultation.appointment.save()
        
        # Redirect to create prescription
        return redirect('prescriptions:create_prescription', appointment_id=consultation.appointment.id)
    
    return redirect('patients:dashboard')
