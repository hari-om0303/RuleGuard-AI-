import os

def generate_pdf():
    pdf_dir = os.path.join(os.path.dirname(__file__), "..", "data", "pdf")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, "emergency_and_special_provisions.pdf")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=54,
            leftMargin=54,
            topMargin=54,
            bottomMargin=54
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#1e3a8a'), spaceAfter=12
        )
        h2_style = ParagraphStyle(
            'SectionH2', parent=styles['Heading2'], fontSize=14, leading=18, textColor=colors.HexColor('#1d4ed8'), spaceBefore=14, spaceAfter=6
        )
        h3_style = ParagraphStyle(
            'SectionH3', parent=styles['Heading3'], fontSize=11, leading=15, textColor=colors.HexColor('#0f172a'), spaceBefore=10, spaceAfter=4
        )
        body_style = ParagraphStyle(
            'BodyDark', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#334155'), spaceAfter=8
        )

        story = [
            Paragraph("Northbridge Institute of Technology", title_style),
            Paragraph("Emergency & Special Provisions Handbook (2025-2026)", h2_style),
            Paragraph("Document Code: NIT-EMERG-2025-v1 | Issuing Authority: Senate Executive Committee", body_style),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=8, spaceAfter=12),
            
            Paragraph("Section 16.0 Emergency Provisions & Special Leaves", h2_style),
            Paragraph("Section 16.1 Formal Medical Leave of Absence", h3_style),
            Paragraph(
                "Students requiring long-term medical treatment or recovery from major illness, surgery, or psychological conditions "
                "may apply for a formal Leave of Absence (LOA) for up to two consecutive regular semesters without losing their degree "
                "registration status. The LOA request must be accompanied by comprehensive medical records certified by the Head of "
                "the NIT Student Health Center and approved by the Academic Steering Committee. Duration spent on an approved LOA "
                "is excluded from the maximum degree completion duration allowance.",
                body_style
            ),
            Paragraph("Section 16.2 Maternity, Paternity & Caregiver Leaves", h3_style),
            Paragraph(
                "Enrolled postgraduate and undergraduate students are entitled to maternity leave of up to sixteen (16) weeks or "
                "paternity leave of up to four (4) weeks upon submission of official medical documentation and birth certificates. "
                "During approved parental leave, student status remains active, academic deadlines are frozen, and students may apply "
                "for deferred course evaluations without penalty.",
                body_style
            ),
            Paragraph("Section 16.3 Defense & Sports Exemption Protocol", h3_style),
            Paragraph(
                "Students selected to represent the country or state in official national sports tournaments or national defense duty "
                "during examination periods are granted duty leave and special makeup examinations without academic penalty. Official "
                "selection letters must be submitted to the Dean of Student Affairs at least fourteen (14) days prior to the event.",
                body_style
            ),
            Paragraph("Section 16.4 Inter-Institutional Credit Transfer Rules", h3_style),
            Paragraph(
                "Students participating in approved exchange programs at partner universities may transfer up to a maximum of "
                "thirty-two (32) academic credits toward their NIT degree requirements, provided each course passed carries a minimum "
                "grade of 'B' (8.0 Grade Points) or equivalent. All credit transfer requests must be pre-approved by the Departmental "
                "Curriculum Committee prior to departure.",
                body_style
            ),
            Paragraph("Section 16.5 Force Majeure & Online Distance Transition Protocol", h3_style),
            Paragraph(
                "In the event of natural disasters, severe weather emergencies, public health crises, or institutional force majeure "
                "requiring physical campus closure, the Academic Senate reserves the right to transition all classes and evaluations to online "
                "distance learning formats. Attendance requirements under Section 4.0 may be relaxed by Executive Decree during force majeure.",
                body_style
            )
        ]
        doc.build(story)
        print(f"Successfully generated PDF using ReportLab at: {pdf_path}")
    except ImportError:
        print("ReportLab not available. Creating minimal standard PDF structure using pure Python...")
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj\n"
            b"2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj\n"
            b"3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources <</Font <</F1 4 0 R>>>> /Contents 5 0 R>> endobj\n"
            b"4 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj\n"
            b"5 0 obj <</Length 900>> stream\n"
            b"BT /F1 14 Tf 50 740 Td (Northbridge Institute of Technology) Tj ET\n"
            b"BT /F1 12 Tf 50 710 Td (Emergency & Special Provisions Handbook) Tj ET\n"
            b"BT /F1 10 Tf 50 680 Td (Section 16.0 Emergency Provisions & Special Leaves) Tj ET\n"
            b"BT /F1 9 Tf 50 650 Td (Section 16.1 Formal Medical Leave of Absence: Long-term medical LOA up to two semesters.) Tj ET\n"
            b"BT /F1 9 Tf 50 620 Td (Section 16.2 Maternity and Paternity Leaves: 16 weeks maternity, 4 weeks paternity.) Tj ET\n"
            b"BT /F1 9 Tf 50 590 Td (Section 16.3 Defense & Sports Exemption Protocol: Duty leave for national sports/defense.) Tj ET\n"
            b"BT /F1 9 Tf 50 560 Td (Section 16.4 Inter-Institutional Credit Transfer Rules: Max 32 transfer credits with B grade.) Tj ET\n"
            b"BT /F1 9 Tf 50 530 Td (Section 16.5 Force Majeure & Online Distance Transition Protocol: Senate executive decree.) Tj ET\n"
            b"endstream\nendobj\n"
            b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000244 00000 n \n0000000313 00000 n \n"
            b"trailer <</Size 6 /Root 1 0 R>>\nstartxref\n1270\n%%EOF\n"
        )
        with open(pdf_path, "wb") as f:
            f.write(pdf_content)
        print(f"Successfully generated standard PDF at: {pdf_path}")

if __name__ == '__main__':
    generate_pdf()
