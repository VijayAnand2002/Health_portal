from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def patient_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_patient:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Patient role required.")
        return redirect('accounts:dashboard')
    return wrapper

def doctor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_doctor:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Doctor role required.")
        return redirect('accounts:dashboard')
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_system_admin or request.user.is_staff):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Admin privileges required.")
        return redirect('accounts:dashboard')
    return wrapper

def hospital_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_hospital_admin:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Hospital Admin role required.")
        return redirect('accounts:dashboard')
    return wrapper
