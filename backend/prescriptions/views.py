from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from accounts.decorators import doctor_required, patient_required
from appointments.models import Appointment
from .models import Prescription, MedicalRecord
from .forms import PrescriptionForm, MedicalRecordForm
from django.contrib import messages
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from .prescription_pdf import generate_prescription_pdf

@login_required
@doctor_required
def create_prescription_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor__user=request.user)
    
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        medications_json = request.POST.get('medications_data')
        
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.doctor = appointment.doctor
            prescription.patient = appointment.patient
            
            if hasattr(appointment, 'consultation'):
                prescription.consultation = appointment.consultation
                
            if medications_json:
                prescription.medications = json.loads(medications_json)
                
            prescription.save()
            
            # Send prescription email to patient
            try:
                subject = f'Your Prescription from Dr. {prescription.doctor.user.get_full_name()}'
                detail_url = request.build_absolute_uri(
                    reverse('prescriptions:view_prescription', args=[prescription.id])
                )
                
                context = {
                    'prescription': prescription,
                    'detail_url': detail_url,
                }
                
                html_message = render_to_string('emails/prescription_email.html', context)
                plain_message = strip_tags(html_message)
                
                # Generate PDF for attachment
                pdf_content = generate_prescription_pdf(prescription)
                
                email = EmailMessage(
                    subject,
                    plain_message,
                    prescription.doctor.user.email,
                    [prescription.patient.user.email],
                )
                email.attach(f'prescription_{prescription.id}.pdf', pdf_content, 'application/pdf')
                email.content_subtype = "html"  # Main content is HTML
                email.body = html_message  # Use the HTML content for the body
                
                email.send(fail_silently=False)
                messages.success(request, "Prescription saved and sent to patient's email.")
            except Exception as e:
                messages.success(request, "Prescription saved and shared with the patient.")
                messages.warning(request, f"Failed to send email: {str(e)}")
            
            return redirect('doctors:dashboard')
    else:
        form = PrescriptionForm()
        
    return render(request, 'prescriptions/create_prescription.html', {
        'form': form, 
        'appointment': appointment
    })

@login_required
def view_prescription_view(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Check authorization
    is_doctor = request.user == prescription.doctor.user
    is_patient = request.user == prescription.patient.user
    
    if not is_doctor:
        if not is_patient or prescription.is_private:
            messages.error(request, "Access denied.")
            return redirect('accounts:dashboard')
        
    return render(request, 'prescriptions/view_prescription.html', {'prescription': prescription})

@login_required
@patient_required
def patient_records_view(request):
    records = MedicalRecord.objects.filter(patient__user=request.user).order_by('-created_at')
    prescriptions = Prescription.objects.filter(patient__user=request.user).order_by('-created_at')
    
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, request.FILES)
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = request.user.patient_profile
            record.uploaded_by = request.user
            record.save()
            messages.success(request, "Medical record uploaded successfully.")
            return redirect('prescriptions:patient_records')
    else:
        form = MedicalRecordForm()
        
    return render(request, 'prescriptions/medical_records.html', {
        'records': records,
        'prescriptions': prescriptions,
        'form': form,
    })


@login_required
def download_prescription_pdf(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    
    # Authorization check
    if request.user != prescription.patient.user and request.user != prescription.doctor.user:
        messages.error(request, "Access denied.")
        return redirect('accounts:dashboard')
        
    pdf_content = generate_prescription_pdf(prescription)
    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}.pdf"'
    return response
