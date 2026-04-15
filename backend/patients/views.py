from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import patient_required
from appointments.models import Appointment
from hospitals.models import Hospital
from doctors.models import DoctorProfile
from .models import PatientProfile
from .forms import PatientPersonalDetailsForm, PatientMedicalHistoryForm
from django.contrib import messages

from django.utils import timezone

@login_required
def dashboard_view(request):
    if not request.user.is_patient:
        return redirect('accounts:dashboard')
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(patient__user=request.user).order_by('-appointment_date')[:10]
    
    # Check for active consultations
    from consultations.models import Consultation
    active_consultations = Consultation.objects.filter(
        appointment__patient__user=request.user,
        status='ACTIVE'
    ).values_list('appointment_id', 'room_id')
    
    # Create a mapping of appointment_id to room_id for easy lookup in template
    active_rooms = {app_id: room_id for app_id, room_id in active_consultations}
    
    # Get the next upcoming consultation appointment (Confirmed Video/Audio)
    upcoming_consultation = Appointment.objects.filter(
        patient__user=request.user,
        status='CONFIRMED',
        consultation_type__in=['VIDEO', 'AUDIO'],
        appointment_date__gte=timezone.now().date()
    ).order_by('appointment_date', 'appointment_time').first()
    
    context = {
        'recent_appointments': recent_appointments,
        'total_appointments': Appointment.objects.filter(patient__user=request.user).count(),
        'active_rooms': active_rooms,
        'upcoming_consultation': upcoming_consultation,
    }
    return render(request, 'patients/dashboard.html', context)
    

@login_required
@patient_required
def search_hospitals_view(request):
    query = request.GET.get('q', '')
    city = request.GET.get('city', '')
    
    hospitals = Hospital.objects.filter(is_active=True, is_verified=True)
    
    if query:
        hospitals = hospitals.filter(name__icontains=query)
    if city:
        hospitals = hospitals.filter(city__icontains=city)
        
    cities = Hospital.objects.values_list('city', flat=True).distinct()
    
    context = {
        'hospitals': hospitals,
        'query': query,
        'city': city,
        'cities': cities,
    }
    return render(request, 'patients/search_hospitals.html', context)

@login_required
@patient_required
def hospital_doctors_view(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = hospital.doctors.filter(is_available=True, is_verified=True)
    
    context = {
        'hospital': hospital,
        'doctors': doctors,
    }
    return render(request, 'patients/hospital_doctors.html', context)

@login_required
@patient_required
def search_doctors_view(request):
    query = request.GET.get('q', '')
    specialization = request.GET.get('specialization', '')
    
    doctors = DoctorProfile.objects.filter(user__is_approved=True, user__is_active=True)
    
    if query:
        doctors = doctors.filter(user__username__icontains=query) | doctors.filter(user__first_name__icontains=query) | doctors.filter(user__last_name__icontains=query)
    if specialization:
        doctors = doctors.filter(specialization__icontains=specialization)
        
    spec_list = DoctorProfile.objects.values_list('specialization', flat=True).distinct()
    specializations = [{'name': s, 'selected': s == specialization} for s in spec_list]
    
    context = {
        'doctors': doctors,
        'query': query,
        'specialization': specialization,
        'specializations': specializations,
    }
    return render(request, 'patients/search_doctors.html', context)

@login_required
@patient_required
def patient_profile_view(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    return render(request, 'patients/profile.html', {'profile': profile})

@login_required
@patient_required
def edit_personal_details_view(request):
    if request.method == 'POST':
        form = PatientPersonalDetailsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Personal details updated successfully.")
            return redirect('patients:profile')
    else:
        form = PatientPersonalDetailsForm(instance=request.user)
    
    return render(request, 'patients/edit_personal_details.html', {'form': form})

@login_required
@patient_required
def update_medical_history_view(request):
    profile, created = PatientProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PatientMedicalHistoryForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical history updated successfully.")
            return redirect('patients:profile')
    else:
        form = PatientMedicalHistoryForm(instance=profile)
    
    return render(request, 'patients/update_medical_history.html', {'form': form})
