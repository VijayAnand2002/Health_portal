from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import admin_required
from accounts.models import User
from hospitals.models import Hospital
from doctors.models import DoctorProfile, DoctorAvailability
from appointments.models import Appointment
from payments.models import Payment
from django.db.models import Sum
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse

@login_required
@admin_required
def dashboard_view(request):
    context = {
        'total_users': User.objects.count(),
        'total_patients': User.objects.filter(role='PATIENT').count(),
        'total_doctors': User.objects.filter(role='DOCTOR').count(),
        'pending_hospitals': Hospital.objects.filter(is_verified=False).count(),
        'pending_doctors': User.objects.filter(role='DOCTOR', is_approved=False).count(),
        'total_revenue': Payment.objects.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0,
        'recent_appointments': Appointment.objects.all().order_by('-created_at')[:5],
        'recent_payments': Payment.objects.all().order_by('-created_at')[:5],
        'recent_doctors': User.objects.filter(role='DOCTOR').order_by('-date_joined')[:5],
        'recent_patients': User.objects.filter(role='PATIENT').order_by('-date_joined')[:5],
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@login_required
@admin_required
def manage_users_view(request):
    """General user management landing page"""
    return render(request, 'admin_dashboard/manage_users.html', {
        'total_doctors': User.objects.filter(role='DOCTOR').count(),
        'total_patients': User.objects.filter(role='PATIENT').count(),
        'total_staff': User.objects.filter(role__in=['SYSTEM_ADMIN', 'HOSPITAL_ADMIN']).count(),
    })

@login_required
@admin_required
def manage_doctors_view(request):
    doctors = User.objects.filter(role='DOCTOR').order_by('-date_joined')
    return render(request, 'admin_dashboard/manage_doctors.html', {'doctors': doctors})

@login_required
@admin_required
def manage_patients_view(request):
    patients = User.objects.filter(role='PATIENT').order_by('-date_joined')
    return render(request, 'admin_dashboard/manage_patients.html', {'patients': patients})

@login_required
@admin_required
def manage_staff_view(request):
    staff = User.objects.filter(role__in=['SYSTEM_ADMIN', 'HOSPITAL_ADMIN']).order_by('-date_joined')
    return render(request, 'admin_dashboard/manage_staff.html', {'staff': staff})

@login_required
@admin_required
def approve_doctor_view(request, user_id):
    user = get_object_or_404(User, id=user_id, role='DOCTOR')
    user.is_approved = True
    user.save()
    
    # Send approval email to doctor
    subject = 'Your Doctor Profile has been Approved!'
    login_url = request.build_absolute_uri(reverse('accounts:login'))
    
    context = {
        'user': user,
        'login_url': login_url,
    }
    
    html_message = render_to_string('emails/doctor_approved.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject,
            plain_message,
            'noreply@healthcareportal.com',
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        messages.success(request, f"Doctor {user.get_full_name()} approved and notification sent.")
    except Exception as e:
        messages.warning(request, f"Doctor approved, but failed to send email: {str(e)}")
        
    return redirect('admin_dashboard:manage_users')

@login_required
@admin_required
def verify_hospital_view(request, hospital_id):
    hospital = get_object_or_404(Hospital, id=hospital_id)
    hospital.is_verified = True
    hospital.save()
    return redirect('admin_dashboard:manage_hospitals')

@login_required
@admin_required
def manage_hospitals_view(request):
    hospitals = Hospital.objects.all().order_by('-created_at')
    return render(request, 'admin_dashboard/manage_hospitals.html', {'hospitals': hospitals})

@login_required
@admin_required
def toggle_user_status_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot suspend your own account.")
    else:
        user.is_active = not user.is_active
        user.save()
        status = "activated" if user.is_active else "suspended"
        messages.success(request, f"User {user.username} has been {status}.")
    return redirect('admin_dashboard:manage_users')

@login_required
@admin_required
def review_doctor_view(request, user_id):
    user = get_object_or_404(User, id=user_id, role='DOCTOR')
    doctor_profile = get_object_or_404(DoctorProfile, user=user)
    
    # Fetch doctor availability
    availability = DoctorAvailability.objects.filter(doctor=doctor_profile).order_by('day')
    
    # Sort availability to follow week order
    days_order = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    sorted_availability = sorted(availability, key=lambda x: days_order.index(x.day))

    return render(request, 'admin_dashboard/review_doctor.html', {
        'target_user': user,
        'profile': doctor_profile,
        'availability': sorted_availability
    })

