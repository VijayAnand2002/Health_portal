from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_required
from .models import DoctorProfile, DoctorAvailability
from .forms import DoctorProfileForm, DoctorUserForm
from appointments.models import Appointment
from django.contrib import messages
from django.db.models import Sum, Count
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse

@login_required
@doctor_required
def dashboard_view(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    
    # Get today's appointments
    from datetime import date
    today_appointments = Appointment.objects.filter(
        doctor=doctor, 
        appointment_date=date.today(),
        status__in=['PENDING', 'CONFIRMED']
    ).order_by('appointment_time')
    
    # Calculate stats
    all_doctor_appointments = Appointment.objects.filter(doctor=doctor)
    total_appointments = all_doctor_appointments.count()
    completed_appointments = all_doctor_appointments.filter(status='COMPLETED').count()
    
    total_earnings = all_doctor_appointments.filter(is_paid=True).aggregate(Sum('consultation_fee'))['consultation_fee__sum'] or 0
    
    completion_rate = 0
    if total_appointments > 0:
        completion_rate = round((completed_appointments / total_appointments) * 100)
    
    rating_percentage = 100
    if doctor.rating:
        rating_percentage = float(doctor.rating) * 20
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
        'pending_list': all_doctor_appointments.filter(status='PENDING').order_by('appointment_date', 'appointment_time')[:3],
        'total_appointments': total_appointments,
        'pending_appointments': all_doctor_appointments.filter(status='PENDING').count(),
        'total_earnings': total_earnings,
        'completion_rate': completion_rate,
        'rating_percentage': rating_percentage,
    }
    return render(request, 'doctors/dashboard_v2.html', context)

@login_required
@doctor_required
def manage_appointments_view(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'doctors/appointments.html', {'appointments': appointments})

@login_required
@doctor_required
def pending_appointments_view(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    pending_list = Appointment.objects.filter(doctor=doctor, status='PENDING').order_by('appointment_date', 'appointment_time')
    
    return render(request, 'doctors/pending_appointments_v2.html', {'pending_list': pending_list})

@login_required
@doctor_required
def approve_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    
    if request.method == 'POST':
        time_str = request.POST.get('appointment_time')
        if time_str:
            appointment.appointment_time = time_str
            appointment.status = 'CONFIRMED'
            appointment.save()
            
            # Send confirmation email to patient
            subject = f'Appointment Confirmed: Dr. {appointment.doctor.user.get_full_name()}'
            detail_url = request.build_absolute_uri(
                reverse('appointments:appointment_detail', args=[appointment.id])
            )
            
            context = {
                'appointment': appointment,
                'detail_url': detail_url,
            }
            
            # Use HTML template for email
            html_message = render_to_string('emails/appointment_confirmed.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    appointment.doctor.user.email,
                    [appointment.patient.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f"Appointment for {appointment.patient.user.get_full_name()} confirmed and notification sent.")
            except Exception as e:
                messages.warning(request, f"Appointment confirmed, but failed to send email: {str(e)}")
        else:
            messages.error(request, "Please provide a consultation time.")
    else:
        messages.warning(request, "Please use the dashboard to approve appointments with a set time.")
        
    return redirect(request.META.get('HTTP_REFERER', 'doctors:dashboard'))

@login_required
@doctor_required
def reject_appointment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    
    if request.method == 'POST':
        appointment.status = 'CANCELLED'
        appointment.save()
        messages.warning(request, f"Appointment for {appointment.patient.user.get_full_name()} has been rejected.")
    
    return redirect(request.META.get('HTTP_REFERER', 'doctors:dashboard'))

@login_required
@doctor_required
def complete_profile_view(request):
    doctor, created = DoctorProfile.objects.get_or_create(user=request.user)
    
    # If profile is already complete and verified, go to dashboard
    if doctor.license_number and request.user.is_approved:
        return redirect('doctors:dashboard')
        
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            
            # Save initial availability if provided
            start_time = form.cleaned_data.get('start_time')
            end_time = form.cleaned_data.get('end_time')
            days_of_week = form.cleaned_data.get('days_of_week')
            
            if start_time and end_time and days_of_week:
                for day in days_of_week:
                    DoctorAvailability.objects.update_or_create(
                        doctor=doctor,
                        day=day,
                        defaults={
                            'is_available': True,
                            'start_time': start_time,
                            'end_time': end_time
                        }
                    )
            
            messages.success(request, "Profile details submitted. Please wait for admin approval.")
            return redirect('doctors:pending_approval')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    return render(request, 'doctors/complete_profile.html', {'form': form})

@login_required
@doctor_required
def pending_approval_view(request):
    if request.user.is_approved:
        return redirect('doctors:dashboard')
    return render(request, 'doctors/pending_approval.html')

@login_required
@doctor_required
def manage_availability_view(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    
    if request.method == 'POST':
        day_index = int(request.POST.get('day'))
        day_name = days[day_index]
        is_available = request.POST.get('is_available') == 'on'
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        copy_all = request.POST.get('copy_all') == 'on'
        
        if copy_all:
            for d in days:
                DoctorAvailability.objects.update_or_create(
                    doctor=doctor,
                    day=d,
                    defaults={
                        'is_available': is_available,
                        'start_time': start_time if is_available else '09:00:00',
                        'end_time': end_time if is_available else '17:00:00'
                    }
                )
            messages.success(request, f"Availability for all days updated.")
        else:
            availability, created = DoctorAvailability.objects.update_or_create(
                doctor=doctor,
                day=day_name,
                defaults={
                    'is_available': is_available,
                    'start_time': start_time if is_available else '09:00:00',
                    'end_time': end_time if is_available else '17:00:00'
                }
            )
            messages.success(request, f"Availability for {day_name.capitalize()} updated.")
        
        return redirect('doctors:manage_availability')

    # Get availability for each day
    availability_records = doctor.availability.all()
    availability_dict = {record.day: record for record in availability_records}
    
    # Prepare list for template ordered by days
    availability_list = [availability_dict.get(day) for day in days]
    
    return render(request, 'doctors/availability.html', {
        'days': [day.capitalize() for day in days],
        'availability': availability_list
    })

@login_required
@doctor_required
def get_available_slots_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    doctor = appointment.doctor
    date_val = appointment.appointment_date
    day_name = date_val.strftime('%A').upper()
    
    # Get availability for this day
    availability = DoctorAvailability.objects.filter(doctor=doctor, day=day_name, is_available=True).first()
    
    if not availability:
        return JsonResponse({'slots': []})
    
    # Generate slots based on doctor's consultation duration
    slots = []
    duration = doctor.consultation_duration or 30
    
    # Use a dummy date to work with datetime for time calculations
    start_dt = datetime.combine(date_val, availability.start_time)
    end_dt = datetime.combine(date_val, availability.end_time)
    
    # Get existing confirmed appointments for this day (excluding current if it's already confirmed)
    existing_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date=date_val,
        status='CONFIRMED'
    ).exclude(id=appointment_id).values_list('appointment_time', flat=True)
    
    # Convert existing times to string for easy comparison
    existing_times = [t.strftime('%H:%M') for t in existing_appointments if t]
    
    current_dt = start_dt
    while current_dt + timedelta(minutes=duration) <= end_dt:
        slot_time_str = current_dt.strftime('%H:%M')
        if slot_time_str not in existing_times:
            slots.append({
                'time': slot_time_str,
                'display': current_dt.strftime('%I:%M %p')
            })
        current_dt += timedelta(minutes=duration)
    
    return JsonResponse({'slots': slots})


def available_slots_api(request, doctor_id):
    """
    General API to fetch available slots for a specific doctor and date.
    Used by patients during booking.
    """
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return JsonResponse({'error': 'Date is required'}, status=400)
        
    try:
        from datetime import datetime
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)
        
    slots = doctor.get_available_slots(date_obj)
    return JsonResponse({'slots': slots})

@login_required
@doctor_required
def doctor_profile_view(request):
    doctor = get_object_or_404(DoctorProfile, user=request.user)
    user = request.user
    
    if request.method == 'POST':
        user_form = DoctorUserForm(request.POST, request.FILES, instance=user)
        profile_form = DoctorProfileForm(request.POST, instance=doctor)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('doctors:doctor_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = DoctorUserForm(instance=user)
        profile_form = DoctorProfileForm(instance=doctor)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'doctor': doctor
    }
    return render(request, 'doctors/profile.html', context)
