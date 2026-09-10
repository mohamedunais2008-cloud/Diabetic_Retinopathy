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


class ReportService:
    @staticmethod
    def generate_pdf_report(
        patient_data: dict,
        screening_data: dict,
        image_paths: dict,
        output_filepath: str
    ) -> str:
        """
        Builds an ophthalmology referral PDF using ReportLab.
        Includes patient history, fundus images, Grad-CAM heatmap, and clinical triage recommendations.
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
        normal = styles['Normal']
        
        # Custom styles
        title_style = ParagraphStyle(
            'HeaderTitle',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f395b"),
            alignment=1
        )
        subtitle_style = ParagraphStyle(
            'HeaderSub',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#4b6584"),
            alignment=1
        )
        section_heading = ParagraphStyle(
            'SectionHead',
            parent=styles['Heading2'],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0f395b"),
            spaceBefore=8,
            spaceAfter=4
        )
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#2f3640")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("<b>NATIONAL TELE-OPHTHALMOLOGY SCREENING PROGRAM</b>", title_style))
        story.append(Paragraph("AI-Assisted Rural Diabetic Retinopathy Triage & Telemedicine Referral (PS 26038)", subtitle_style))
        story.append(Spacer(1, 10))

        # 2. Patient Demographics & Camp Metadata Table
        now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
        demo_data = [
            [
                Paragraph(f"<b>Patient Name:</b> {patient_data.get('full_name', 'N/A')}", body_style),
                Paragraph(f"<b>Patient ID:</b> {patient_data.get('patient_uid', 'N/A')}", body_style),
                Paragraph(f"<b>Age / Sex:</b> {patient_data.get('age', 'N/A')} yrs / {patient_data.get('gender', 'N/A')}", body_style)
            ],
            [
                Paragraph(f"<b>Village / Block:</b> {patient_data.get('village', 'N/A')}", body_style),
                Paragraph(f"<b>District:</b> {patient_data.get('district', 'N/A')}", body_style),
                Paragraph(f"<b>Screening Date:</b> {now_str}", body_style)
            ],
            [
                Paragraph(f"<b>Diabetes Duration:</b> {patient_data.get('diabetes_years', '0')} yrs", body_style),
                Paragraph(f"<b>HbA1c Level:</b> {patient_data.get('hba1c', 'N/A')}%", body_style),
                Paragraph(f"<b>Eye Examined:</b> {screening_data.get('eye', 'OD')}", body_style)
            ]
        ]
        demo_table = Table(demo_data, colWidths=[180, 180, 180])
        demo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f2f6")),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced6e0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dfe4ea")),
        ]))
        story.append(demo_table)
        story.append(Spacer(1, 12))

        # 3. AI Diagnostic Verdict Callout Box
        is_referable = screening_data.get('is_referable', False)
        box_bg = colors.HexColor("#ffcccc") if is_referable else colors.HexColor("#e2f8eb")
        box_border = colors.HexColor("#eb4d4b") if is_referable else colors.HexColor("#2ed573")
        status_text = "REFERABLE DIABETIC RETINOPATHY - URGENT SPECIALIST REVIEW" if is_referable else "NON-REFERABLE (ROUTINE ANNUAL MONITORING)"
        
        triage_data = [
            [
                Paragraph(f"<font size=11 color='{box_border.hexval()}'><b>DIAGNOSTIC STATUS: {status_text}</b></font>", body_style)
            ],
            [
                Paragraph(f"<b>ICDR Classification:</b> {screening_data.get('grade_name', 'N/A')} &nbsp;|&nbsp; <b>Model Confidence:</b> {screening_data.get('confidence_percent', 'N/A')} &nbsp;|&nbsp; <b>Recall Period:</b> {screening_data.get('recall_period', '12 Months')}", body_style)
            ]
        ]
        triage_table = Table(triage_data, colWidths=[540])
        triage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), box_bg),
            ('BOX', (0, 0), (-1, -1), 1.5, box_border),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(triage_table)
        story.append(Spacer(1, 12))

        # 4. Multi-Modal Images Table (Original, Preprocessed CLAHE, Grad-CAM Heatmap)
        story.append(Paragraph("<b>MULTI-MODAL RETINAL IMAGING & EXPLAINABLE AI HEATMAP</b>", section_heading))
        
        img_row = []
        raw_p = image_paths.get("raw")
        prep_p = image_paths.get("preprocessed")
        grad_p = image_paths.get("gradcam")

        # Load images if file exists
        cell_raw = Paragraph("Raw Fundus Photo", body_style)
        cell_prep = Paragraph("Green-Channel CLAHE", body_style)
        cell_grad = Paragraph("Explainable Grad-CAM Heatmap", body_style)

        if raw_p and os.path.exists(raw_p):
            cell_raw = [RLImage(raw_p, width=170, height=170), Paragraph("<font size=8><b>1. Raw Fundus Photo</b></font>", body_style)]
        if prep_p and os.path.exists(prep_p):
            cell_prep = [RLImage(prep_p, width=170, height=170), Paragraph("<font size=8><b>2. Preprocessed (CLAHE)</b></font>", body_style)]
        if grad_p and os.path.exists(grad_p):
            cell_grad = [RLImage(grad_p, width=170, height=170), Paragraph("<font size=8><b>3. Grad-CAM Salience Overlay</b></font>", body_style)]

        img_table = Table([[cell_raw, cell_prep, cell_grad]], colWidths=[180, 180, 180])
        img_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(img_table)
        story.append(Spacer(1, 10))

        # 5. Sub-pixel Lesion Analysis & Clinical XAI Findings
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
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8f9fa")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#ced6e0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dfe4ea")),
        ]))
        story.append(lesion_table)
        story.append(Spacer(1, 10))

        # 6. Clinical Explanation & Referral Directives
        story.append(Paragraph("<b>CLINICAL EXPLANATION & ASHA WORKER ACTION DIRECTIVE</b>", section_heading))
        story.append(Paragraph(f"<b>Explainability Rationale:</b> {screening_data.get('xai_summary', '')}", body_style))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<b>ASHA Worker / PHC Action:</b> {screening_data.get('asha_guidance', '')}", body_style))
        story.append(Spacer(1, 15))

        # 7. Sign-Off Footer
        sign_data = [
            [
                Paragraph("<b>Screened By (PHC Staff / ASHA):</b><br/><br/>___________________________", body_style),
                Paragraph("<b>Reviewing District Ophthalmologist:</b><br/><br/>___________________________", body_style)
            ]
        ]
        sign_table = Table(sign_data, colWidths=[270, 270])
        sign_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(sign_table)

        doc.build(story)
        return output_filepath
