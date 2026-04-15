from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from io import BytesIO

def generate_prescription_pdf(prescription):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    styles.add(ParagraphStyle(name='HospitalName', fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor("#0d6efd"), alignment=1, leading=28))
    styles.add(ParagraphStyle(name='HospitalSubtitle', fontName='Helvetica', fontSize=10, textColor=colors.grey, alignment=1, spaceAfter=20))
    styles.add(ParagraphStyle(name='SectionHeader', fontName='Helvetica-Bold', fontSize=14, spaceBefore=20, spaceAfter=10, textColor=colors.darkgrey))
    
    elements = []
    
    # Header
    elements.append(Paragraph("DIGITAL HEALTH PORTAL", styles['HospitalName']))
    elements.append(Paragraph("Certified Online Medical Consultation", styles['HospitalSubtitle']))
    elements.append(Spacer(1, 10))
    
    # Doctor Info
    doctor_name = f"Dr. {prescription.doctor.user.get_full_name()}"
    elements.append(Paragraph(f"<b>Doctor:</b> {doctor_name}", styles['Normal']))
    elements.append(Paragraph(f"<b>Specialization:</b> {prescription.doctor.specialization}", styles['Normal']))
    elements.append(Paragraph(f"<b>License No:</b> {prescription.doctor.license_number}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {prescription.created_at.strftime('%d %b %Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Patient Info
    elements.append(Paragraph(f"<b>Patient:</b> {prescription.patient.user.get_full_name()}", styles['Normal']))
    
    if prescription.symptoms:
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("<b>Symptoms:</b>", styles['Normal']))
        elements.append(Paragraph(prescription.symptoms, styles['Normal']))
        
    elements.append(Paragraph(f"<b>Diagnosis:</b> {prescription.diagnosis}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Medications Table
    elements.append(Paragraph("MEDICATIONS (Rx)", styles['SectionHeader']))
    data = [['Medication', 'Dosage', 'Frequency', 'Duration']]
    if prescription.medications:
        for med in prescription.medications:
            data.append([med.get('name', ''), med.get('dosage', ''), med.get('frequency', ''), med.get('duration', '')])
    
    table = Table(data, colWidths=[150, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f8f9fa")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)
    
    # Instructions
    elements.append(Paragraph("INSTRUCTIONS", styles['SectionHeader']))
    elements.append(Paragraph(prescription.instructions or "No specific instructions provided.", styles['Normal']))
    
    # Lab Tests
    if prescription.lab_tests:
        elements.append(Paragraph("RECOMMENDED LAB TESTS", styles['SectionHeader']))
        elements.append(Paragraph(prescription.lab_tests, styles['Normal']))

    # Follow-up
    if prescription.follow_up_date:
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"<b>Next Follow-up Date:</b> {prescription.follow_up_date.strftime('%d %b %Y')}", styles['Normal']))
    
    # Footer
    elements.append(Spacer(1, 40))
    
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
