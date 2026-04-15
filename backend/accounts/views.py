from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm
from patients.models import PatientProfile
from doctors.models import DoctorProfile

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            
            # Create profile based on role
            if role == 'PATIENT':
                PatientProfile.objects.create(user=user)
            elif role == 'DOCTOR':
                DoctorProfile.objects.create(user=user)
                user.is_approved = False  # Doctors need approval
                user.save()
            
            login(request, user)
            messages.success(request, f"Account created for {user.username}!")
            return redirect('accounts:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    if request.user.is_patient:
        return redirect('patients:dashboard')
    elif request.user.is_doctor:
        # Check if profile is complete
        try:
            profile = request.user.doctor_profile
            if not profile.license_number:
                return redirect('doctors:complete_profile')
            if not request.user.is_approved:
                return redirect('doctors:pending_approval')
            return redirect('doctors:dashboard')
        except:
            return redirect('doctors:complete_profile')
    elif request.user.is_hospital_admin:
        return redirect('hospitals:dashboard')
    elif request.user.is_system_admin:
        return redirect('admin_dashboard:dashboard')
    return redirect('home')
