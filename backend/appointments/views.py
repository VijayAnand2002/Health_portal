from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentBookingForm
from doctors.models import DoctorProfile, DoctorAvailability
from patients.models import PatientProfile
from django.contrib import messages

@login_required
def book_appointment_view(request, doctor_id):
    if not request.user.is_patient:
        messages.error(request, "Only patients can book appointments.")
        return redirect('accounts:dashboard')
        
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient = get_object_or_404(PatientProfile, user=request.user)
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.doctor = doctor
            appointment.patient = patient
            appointment.consultation_fee = doctor.consultation_fee
            appointment.status = 'PENDING'
            appointment.save()
            
            messages.success(request, f"Appointment request sent to Dr. {doctor.user.get_full_name()}.")
            return redirect('patients:dashboard')
    else:
        form = AppointmentBookingForm()
        
    # Get doctor's availability for the week
    availability = doctor.availability.filter(is_available=True).order_by('day', 'start_time')
    
    context = {
        'form': form,
        'doctor': doctor,
        'availability': availability,
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def appointment_detail_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Simple security check
    if request.user != appointment.patient.user and request.user != appointment.doctor.user:
        messages.error(request, "You are not authorized to view this appointment.")
        return redirect('accounts:dashboard')
        
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def edit_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check: only the patient or the doctor can edit
    if request.user != appointment.patient.user and request.user != appointment.doctor.user:
        messages.error(request, "You are not authorized to edit this appointment.")
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, request.FILES, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Appointment updated successfully.")
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentBookingForm(instance=appointment)
        
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/edit_appointment.html', context)


@login_required
def delete_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check: only the patient or the doctor can delete/cancel
    if request.user != appointment.patient.user and request.user != appointment.doctor.user:
        messages.error(request, "You are not authorized to delete this appointment.")
        return redirect('accounts:dashboard')
        
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment deleted successfully.")
        return redirect('patients:dashboard')
        
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/confirm_delete.html', context)
