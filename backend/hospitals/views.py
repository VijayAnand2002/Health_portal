from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import hospital_admin_required
from .models import Hospital
from .forms import HospitalProfileForm, AddDoctorForm
from doctors.models import DoctorProfile
from appointments.models import Appointment
from django.db.models import Count, Sum

@login_required
@hospital_admin_required
def dashboard_view(request):
    # Get the hospital managed by this admin
    hospital = get_object_or_404(Hospital, admin=request.user)
    
    # Get doctors affiliated with this hospital
    doctors = hospital.doctors.all()
    
    # Get appointments for these doctors
    appointments = Appointment.objects.filter(doctor__in=doctors).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'hospital': hospital,
        'doctors': doctors,
        'recent_appointments': appointments[:5],
        'total_doctors': doctors.count(),
        'total_appointments': appointments.count(),
        'pending_appointments': appointments.filter(status='PENDING').count(),
        'confirmed_appointments': appointments.filter(status='CONFIRMED').count(),
        'total_revenue': appointments.filter(is_paid=True).aggregate(Sum('consultation_fee'))['consultation_fee__sum'] or 0,
    }
    
    return render(request, 'hospitals/dashboard.html', context)

@login_required
@hospital_admin_required
def manage_doctors_view(request):
    hospital = get_object_or_404(Hospital, admin=request.user)
    doctors = hospital.doctors.all()
    
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        action = request.POST.get('action')
        doctor = get_object_or_404(DoctorProfile, id=doctor_id)
        
        if action == 'remove':
            hospital.doctors.remove(doctor)
            messages.success(request, f"Dr. {doctor.user.get_full_name()} removed from hospital.")
        elif action == 'verify':
            doctor.is_verified = True
            doctor.save()
            messages.success(request, f"Dr. {doctor.user.get_full_name()} has been verified.")
        elif action == 'unverify':
            doctor.is_verified = False
            doctor.save()
            messages.success(request, f"Dr. {doctor.user.get_full_name()} verification revoked.")
            
        return redirect('hospitals:manage_doctors')
        
    return render(request, 'hospitals/manage_doctors.html', {
        'hospital': hospital,
        'doctors': doctors
    })

@login_required
@hospital_admin_required
def edit_hospital_profile_view(request):
    hospital = get_object_or_404(Hospital, admin=request.user)
    
    if request.method == 'POST':
        form = HospitalProfileForm(request.POST, request.FILES, instance=hospital)
        if form.is_valid():
            form.save()
            messages.success(request, "Hospital profile updated successfully.")
            return redirect('hospitals:dashboard')
    else:
        form = HospitalProfileForm(instance=hospital)
        
    return render(request, 'hospitals/edit_profile.html', {
        'form': form,
        'hospital': hospital
    })

@login_required
@hospital_admin_required
def add_doctor_view(request):
    hospital = get_object_or_404(Hospital, admin=request.user)
    
    if request.method == 'POST':
        form = AddDoctorForm(request.POST)
        if form.is_valid():
            license_number = form.cleaned_data['license_number']
            try:
                doctor = DoctorProfile.objects.get(license_number=license_number)
                hospital.doctors.add(doctor)
                messages.success(request, f"Dr. {doctor.user.get_full_name()} added to your hospital.")
                return redirect('hospitals:manage_doctors')
            except DoctorProfile.DoesNotExist:
                messages.error(request, "Doctor with this license number not found.")
    else:
        form = AddDoctorForm()
        
    return render(request, 'hospitals/add_doctor.html', {
        'form': form,
        'hospital': hospital
    })
@login_required
@hospital_admin_required
def hospital_appointments_view(request):
    hospital = get_object_or_404(Hospital, admin=request.user)
    doctors = hospital.doctors.all()
    appointments = Appointment.objects.filter(doctor__in=doctors).order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'hospitals/appointments.html', {
        'hospital': hospital,
        'appointments': appointments
    })

@login_required
@hospital_admin_required
def approve_appointment_view(request, appointment_id):
    hospital = get_object_or_404(Hospital, admin=request.user)
    doctors = hospital.doctors.all()
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__in=doctors)
    
    if request.method == 'POST':
        time_str = request.POST.get('appointment_time')
        if time_str:
            appointment.appointment_time = time_str
            appointment.status = 'CONFIRMED'
            appointment.save()
            messages.success(request, f"Appointment for {appointment.patient.user.get_full_name()} confirmed at {time_str}.")
        else:
            messages.error(request, "Please provide a consultation time.")
            
    return redirect(request.META.get('HTTP_REFERER', 'hospitals:dashboard'))

@login_required
@hospital_admin_required
def reject_appointment_view(request, appointment_id):
    hospital = get_object_or_404(Hospital, admin=request.user)
    doctors = hospital.doctors.all()
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__in=doctors)
    
    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.warning(request, f"Appointment for {appointment.patient.user.get_full_name()} has been rejected.")
        
    return redirect(request.META.get('HTTP_REFERER', 'hospitals:dashboard'))
