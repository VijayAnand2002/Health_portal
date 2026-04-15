from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from appointments.models import Appointment
from payments.models import Payment
from django.db.models.functions import TruncDate
from django.db.models import Count, Sum
import json
from datetime import timedelta
from django.utils import timezone

@login_required
@admin_required
def reports_view(request):
    # Last 7 days statistics
    last_week = timezone.now() - timedelta(days=7)
    
    appointment_stats = Appointment.objects.filter(created_at__gte=last_week) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')
        
    revenue_stats = Payment.objects.filter(status='COMPLETED', created_at__gte=last_week) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(total=Sum('amount')) \
        .order_by('date')
        
    # Prepare data for Chart.js
    labels = [(last_week + timedelta(days=i)).strftime('%d %b') for i in range(8)]
    apt_data = [0] * 8
    rev_data = [0] * 8
    
    for i in range(8):
        current_date = (last_week + timedelta(days=i)).date()
        for stat in appointment_stats:
            if stat['date'] == current_date:
                apt_data[i] = stat['count']
        for stat in revenue_stats:
            if stat['date'] == current_date:
                rev_data[i] = float(stat['total'])

    context = {
        'labels_json': json.dumps(labels),
        'apt_data_json': json.dumps(apt_data),
        'rev_data_json': json.dumps(rev_data),
        'total_revenue': Payment.objects.filter(status='COMPLETED').aggregate(Sum('amount'))['amount__sum'] or 0,
        'total_appointments': Appointment.objects.count(),
    }
    return render(request, 'analytics/reports.html', context)
