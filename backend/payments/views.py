import stripe
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json

from appointments.models import Appointment
from consultations.models import Consultation
from .models import Payment
import uuid

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def initiate_payment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    
    if appointment.is_paid:
        return redirect('patients:dashboard')
        
    context = {
        'appointment': appointment,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'payments/process.html', context)

@login_required
def create_checkout_session(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient__user=request.user)
    
    if appointment.is_paid:
        return JsonResponse({'error': 'Appointment already paid'})
        
    domain_url = request.build_absolute_uri('/')[:-1]
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(appointment.consultation_fee * 100),
                        'product_data': {
                            'name': f'Consultation with Dr. {appointment.doctor.user.get_full_name()}',
                        },
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=domain_url + reverse('payments:success') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=domain_url + reverse('payments:cancel'),
            client_reference_id=str(appointment.id),
            metadata={
                'appointment_id': appointment.id,
                'patient_id': appointment.patient.id,
            }
        )
        return JsonResponse({'sessionId': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)})

@login_required
def payment_success_view(request):
    session_id = request.GET.get('session_id')
    payment = None
    
    if session_id:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            # Process payment in case webhook hasn't fired yet
            handle_checkout_session(session)
            
            # Retrieve payment record to pass to template
            appointment_id = session.get('client_reference_id')
            if appointment_id:
                payment = Payment.objects.filter(
                    appointment_id=appointment_id,
                    status='COMPLETED'
                ).first()
        except Exception:
            pass
    
    context = {'payment': payment}
    return render(request, 'payments/success.html', context)

@login_required
def payment_cancel_view(request):
    return render(request, 'payments/cancel.html')

@login_required
def download_receipt(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.colors import HexColor
    from reportlab.pdfgen import canvas as pdf_canvas
    from io import BytesIO
    
    buffer = BytesIO()
    c = pdf_canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Colors
    primary = HexColor('#0d6efd')
    dark = HexColor('#212529')
    muted = HexColor('#6c757d')
    light_bg = HexColor('#f8f9fa')
    
    # Header background
    c.setFillColor(primary)
    c.rect(0, height - 100, width, 100, fill=True, stroke=False)
    
    # Header text
    c.setFillColor(HexColor('#ffffff'))
    c.setFont('Helvetica-Bold', 22)
    c.drawString(40, height - 50, 'HealthCare Portal')
    c.setFont('Helvetica', 11)
    c.drawString(40, height - 70, 'Payment Receipt')
    
    # Receipt number on right
    c.setFont('Helvetica-Bold', 11)
    c.drawRightString(width - 40, height - 50, f'Receipt #{payment.id}')
    c.setFont('Helvetica', 10)
    c.drawRightString(width - 40, height - 70, f'Date: {payment.paid_at.strftime("%d %b %Y, %I:%M %p") if payment.paid_at else payment.created_at.strftime("%d %b %Y, %I:%M %p")}')
    
    y = height - 140
    
    # Divider line
    c.setStrokeColor(HexColor('#dee2e6'))
    c.setLineWidth(0.5)
    c.line(40, y, width - 40, y)
    y -= 30
    
    # Patient & Doctor Info
    c.setFillColor(dark)
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, 'Patient:')
    c.setFont('Helvetica', 12)
    c.drawString(130, y, payment.user.get_full_name() or payment.user.username)
    y -= 25
    
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, 'Doctor:')
    c.setFont('Helvetica', 12)
    doctor_name = f'Dr. {payment.appointment.doctor.user.get_full_name()}'
    c.drawString(130, y, doctor_name)
    y -= 25
    
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, 'Date:')
    c.setFont('Helvetica', 12)
    appt = payment.appointment
    appt_str = appt.appointment_date.strftime('%d %b %Y')
    if appt.appointment_time:
        appt_str += f' at {appt.appointment_time.strftime("%H:%M")}'
    c.drawString(130, y, appt_str)
    y -= 25
    
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40, y, 'Type:')
    c.setFont('Helvetica', 12)
    c.drawString(130, y, appt.get_consultation_type_display())
    y -= 40
    
    # Divider
    c.line(40, y, width - 40, y)
    y -= 30
    
    # Payment details table header
    c.setFillColor(light_bg)
    c.rect(40, y - 5, width - 80, 25, fill=True, stroke=False)
    c.setFillColor(dark)
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Description')
    c.drawRightString(width - 50, y, 'Amount')
    y -= 30
    
    # Line item
    c.setFont('Helvetica', 11)
    c.setFillColor(dark)
    c.drawString(50, y, f'Consultation Fee - {doctor_name}')
    c.drawRightString(width - 50, y, f'Rs. {payment.amount}')
    y -= 25
    
    c.setFillColor(muted)
    c.drawString(50, y, 'Processing Fee')
    c.drawRightString(width - 50, y, 'Rs. 0.00')
    y -= 20
    
    # Divider
    c.setStrokeColor(primary)
    c.setLineWidth(1)
    c.line(40, y, width - 40, y)
    y -= 25
    
    # Total
    c.setFillColor(primary)
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, 'Total Paid')
    c.drawRightString(width - 50, y, f'Rs. {payment.amount}')
    y -= 40
    
    # Transaction details
    c.setFillColor(muted)
    c.setFont('Helvetica', 9)
    c.drawString(40, y, f'Transaction ID: {payment.transaction_id or "N/A"}')
    y -= 15
    c.drawString(40, y, f'Payment Method: {payment.get_payment_method_display()}')
    y -= 15
    c.drawString(40, y, f'Status: {payment.get_status_display()}')
    y -= 50
    
    # Footer
    c.setStrokeColor(HexColor('#dee2e6'))
    c.setLineWidth(0.5)
    c.line(40, y, width - 40, y)
    y -= 25
    c.setFillColor(muted)
    c.setFont('Helvetica', 9)
    c.drawCentredString(width / 2, y, 'Thank you for choosing HealthCare Portal. This is a computer-generated receipt.')
    
    c.showPage()
    c.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.id}.pdf"'
    return response

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
        
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
        
    return HttpResponse(status=200)

def handle_checkout_session(session):
    appointment_id = session.get('client_reference_id')
    if appointment_id:
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            if not appointment.is_paid:
                appointment.is_paid = True
                appointment.save()
                
                # Create Payment record
                from django.utils import timezone as tz
                Payment.objects.create(
                    appointment=appointment,
                    user=appointment.patient.user,
                    transaction_id=session.get('id'),
                    amount=appointment.consultation_fee,
                    status='COMPLETED',
                    payment_method='STRIPE',
                    paid_at=tz.now(),
                    description=f"Stripe Payment for Appointment {appointment.id}"
                )
                
                # Auto-create consultation room if it's a video/audio consultation
                if appointment.consultation_type in ['VIDEO', 'AUDIO']:
                    Consultation.objects.get_or_create(
                        appointment=appointment,
                        defaults={
                            'room_id': f"room_{uuid.uuid4().hex[:10]}",
                            'status': 'ACTIVE'  # Using 'ACTIVE' to match existing dashboard filter
                        }
                    )
        except Appointment.DoesNotExist:
            pass
