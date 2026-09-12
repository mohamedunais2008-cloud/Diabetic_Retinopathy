"""
Automated Clinical Referral Report Generator (PDF)
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing


class ReportService:
    @staticmethod
    def generate_pdf_report(
        patient_data: dict,
        screening_data: dict,
        image_paths: dict,
        output_filepath: str,
        camp_data: dict = None,
        doctor_data: dict = None
    ) -> str:
        """
        Builds an ophthalmology referral PDF using ReportLab.
        Includes patient history, fundus images, Grad-CAM heatmap, camp GPS stamp,
        sub-pixel lesion findings, Fast-Track QR code, and Doctor digital signature.
        """
        os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
        doc = SimpleDocTemplate(
            output_filepath,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Heading1'],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#0f395b"),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'HeaderSub',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#4b6584"),
            alignment=1
        )
        section_heading = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0f395b"),
            spaceBefore=6,
            spaceAfter=3
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=8.5,
            leading=11.5,
            textColor=colors.HexColor("#2f3640")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("<b>NATIONAL TELE-OPHTHALMOLOGY SCREENING PROGRAM</b>", title_style))
        story.append(Paragraph("AI-Assisted Rural Diabetic Retinopathy Triage & Telemedicine Referral (PS 26038)", subtitle_style))
        story.append(Spacer(1, 8))

        # Camp & GPS Metadata
        camp_info = camp_data or {}
        camp_name = camp_info.get("camp_name", "Primary Health Centre (PHC) Mobile Camp")
        lat = camp_info.get("lat")
        lon = camp_info.get("lon")
        gps_str = f"{lat:.4f}° N, {lon:.4f}° E" if lat and lon else "GPS Lat/Lon Logged"
        img_qual = camp_info.get("image_quality_status", "Good (Clinically Gradable)")

        # 2. Patient Demographics & Camp Metadata Table
        now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
        demo_data = [
            [
                Paragraph(f"<b>Patient Name:</b> {patient_data.get('full_name', 'N/A')}", body_style),
                Paragraph(f"<b>Patient ID:</b> {patient_data.get('patient_uid', 'N/A')}", body_style),
                Paragraph(f"<b>Age / Sex:</b> {patient_data.get('age', 'N/A')} yrs / {patient_data.get('gender', 'N/A')}", body_style)
            ],
            [
                Paragraph(f"<b>Village / District:</b> {patient_data.get('village', 'N/A')}, {patient_data.get('district', 'N/A')}", body_style),
                Paragraph(f"<b>Field Camp:</b> {camp_name}", body_style),
                Paragraph(f"<b>Camp GPS:</b> 📍 {gps_str}", body_style)
            ],
            [
                Paragraph(f"<b>Diabetes Duration:</b> {patient_data.get('diabetes_years', '0')} yrs", body_style),
                Paragraph(f"<b>HbA1c:</b> {patient_data.get('hba1c', 'N/A')}%", body_style),
                Paragraph(f"<b>Eye Examined:</b> {screening_data.get('eye', 'OD')} (Image Quality: {img_qual})", body_style)
            ]
        ]
        demo_table = Table(demo_data, colWidths=[180, 180, 180])
        demo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f2f6")),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced6e0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dfe4ea")),
        ]))
        story.append(demo_table)
        story.append(Spacer(1, 8))

        # 3. AI Diagnostic Verdict Callout Box
        is_referable = screening_data.get('is_referable', False)
        box_bg = colors.HexColor("#ffcccc") if is_referable else colors.HexColor("#e2f8eb")
        box_border = colors.HexColor("#eb4d4b") if is_referable else colors.HexColor("#2ed573")
        status_text = "REFERABLE DIABETIC RETINOPATHY - URGENT SPECIALIST REVIEW REQUIRED" if is_referable else "NON-REFERABLE (ROUTINE ANNUAL PHC MONITORING)"
        
        triage_data = [
            [
                Paragraph(f"<font size=10 color='{box_border.hexval()}'><b>DIAGNOSTIC STATUS: {status_text}</b></font>", body_style)
            ],
            [
                Paragraph(f"<b>ICDR Classification:</b> {screening_data.get('grade_name', 'N/A')} &nbsp;|&nbsp; <b>Model Confidence:</b> {screening_data.get('confidence_percent', 'N/A')} &nbsp;|&nbsp; <b>Recall Period:</b> {screening_data.get('recall_period', '12 Months')}", body_style)
            ]
        ]
        triage_table = Table(triage_data, colWidths=[540])
        triage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), box_bg),
            ('BOX', (0, 0), (-1, -1), 1.5, box_border),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(triage_table)
        story.append(Spacer(1, 8))

        # 4. Multi-Modal Images Table (Original, Preprocessed CLAHE, Grad-CAM Heatmap)
        story.append(Paragraph("<b>MULTI-MODAL RETINAL IMAGING & EXPLAINABLE AI SALIENCY</b>", section_heading))
        
        raw_p = image_paths.get("raw")
        prep_p = image_paths.get("preprocessed")
        grad_p = image_paths.get("gradcam")

        cell_raw = Paragraph("Raw Fundus Photo", body_style)
        cell_prep = Paragraph("Green-Channel CLAHE", body_style)
        cell_grad = Paragraph("Explainable Grad-CAM Heatmap", body_style)

        if raw_p and os.path.exists(raw_p):
            cell_raw = [RLImage(raw_p, width=165, height=140), Paragraph("<font size=7.5><b>1. Raw Fundus Photo</b></font>", body_style)]
        if prep_p and os.path.exists(prep_p):
            cell_prep = [RLImage(prep_p, width=165, height=140), Paragraph("<font size=7.5><b>2. Preprocessed (CLAHE)</b></font>", body_style)]
        if grad_p and os.path.exists(grad_p):
            cell_grad = [RLImage(grad_p, width=165, height=140), Paragraph("<font size=7.5><b>3. Grad-CAM Salience Overlay</b></font>", body_style)]

        img_table = Table([[cell_raw, cell_prep, cell_grad]], colWidths=[180, 180, 180])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 6))

        # 5. Sub-pixel Lesion Analysis
        findings = screening_data.get("pathology_findings", {})
        story.append(Paragraph("<b>SUB-PIXEL MICROVASCULAR LESION DETECTION</b>", section_heading))
        
        lesion_data = [
            ["Microaneurysms", "Dot / Blot Hemorrhages", "Hard Exudates", "Cotton Wool Spots", "Neovascularization"],
            [
                str(findings.get("microaneurysms", 0)),
                str(findings.get("hemorrhages", 0)),
                str(findings.get("hard_exudates", 0)),
                str(findings.get("cotton_wool_spots", 0)),
                str(findings.get("neovascularization", "Absent"))
            ]
        ]
        lesion_table = Table(lesion_data, colWidths=[108, 108, 108, 108, 108])
        lesion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f395b")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8f9fa")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced6e0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dfe4ea")),
        ]))
        story.append(lesion_table)
        story.append(Spacer(1, 6))

        # 6. Clinical Explanation & Referral Directives
        story.append(Paragraph("<b>EXPLAINABLE AI CLINICAL RATIONALE & TRIAGE DIRECTIVE</b>", section_heading))
        story.append(Paragraph(f"<b>Pathology Findings:</b> {screening_data.get('xai_summary', '')}", body_style))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>ASHA Worker / PHC Directive:</b> {screening_data.get('asha_guidance', '')}", body_style))
        story.append(Spacer(1, 6))

        # 7. Fast-Track QR Code + Doctor Digital Certification
        doc_info = doctor_data or {}
        signed_by = doc_info.get("doctor_signed_by")
        action = doc_info.get("doctor_clinical_action", "Pending Tele-Ophthalmology Review")
        rx = doc_info.get("doctor_prescription", "")

        # Generate QR Code Drawing
        screening_uid = screening_data.get("screening_uid", "SCR-REF")
        qr_content = f"RETINAAI-REF|PAT:{patient_data.get('patient_uid')}|NAME:{patient_data.get('full_name')}|GRADE:{screening_data.get('grade_name')}|URGENCY:{screening_data.get('urgency', 'Normal')}"
        qr_widget = qr.QrCodeWidget(qr_content)
        bounds = qr_widget.getBounds()
        w = bounds[2] - bounds[0]
        h = bounds[3] - bounds[1]
        qr_drawing = Drawing(65, 65, transform=[65.0 / w, 0, 0, 65.0 / h, 0, 0])
        qr_drawing.add(qr_widget)

        if signed_by:
            doctor_block = [
                Paragraph(f"<font color='#0a7ea4'><b>✓ DIGITALLY CERTIFIED BY SPECIALIST</b></font>", body_style),
                Paragraph(f"<b>Ophthalmologist:</b> {signed_by}", body_style),
                Paragraph(f"<b>Clinical Action:</b> {action}", body_style),
                Paragraph(f"<b>Prescription / Advice:</b> {rx or 'Follow hospital laser / medical guidelines'}", body_style),
                Paragraph(f"<font size=7 color='#6c757d'>Signed electronically via RetinaAI Telemedicine Gateway</font>", body_style)
            ]
        else:
            doctor_block = [
                Paragraph("<b>Reviewing District Ophthalmologist:</b>", body_style),
                Spacer(1, 15),
                Paragraph("__________________________________________<br/><font size=7 color='#6c757d'>Signature & Reg. No. / Digital Token</font>", body_style)
            ]

        qr_block = [
            qr_drawing,
            Paragraph("<font size=7><b>Fast-Track Referral QR</b><br/>Scan at District Hospital</font>", body_style)
        ]

        sign_data = [
            [
                Paragraph("<b>Screened By (PHC Staff / ASHA):</b><br/><br/>___________________________<br/><font size=7 color='#6c757d'>Camp Operator Verified</font>", body_style),
                doctor_block,
                qr_block
            ]
        ]
        sign_table = Table(sign_data, colWidths=[180, 260, 100])
        sign_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced6e0")),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sign_table)

        doc.build(story)
        return output_filepath
