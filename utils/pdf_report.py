from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

import os
from datetime import datetime

# Optional font (Windows)
try:
    pdfmetrics.registerFont(
        TTFont("Arial", "C:/Windows/Fonts/arial.ttf")
    )
    FONT_NAME = "Arial"
except:
    FONT_NAME = "Helvetica"


def _draw_page_chrome(canvas, document):
    canvas.saveState()
    width, height = document.pagesize
    canvas.setFillColor(colors.HexColor("#0F172A"))
    canvas.rect(0, height - 22, width, 22, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
    canvas.line(document.leftMargin, 28, width - document.rightMargin, 28)
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor("#64748B"))
    canvas.drawString(document.leftMargin, 16, "Traffic Intelligence | Confidential")
    canvas.drawRightString(width - document.rightMargin, 16, f"Page {document.page}")
    canvas.restoreState()


def generate_pdf_report(
    file_path,
    username,
    kpis,
    insights,
    recommendations
):
    """
    Generates a polished, executive-ready PDF report for business stakeholders.
    """

    styles = getSampleStyleSheet()

    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    title_style.fontName = FONT_NAME
    title_style.fontSize = 22
    title_style.leading = 28

    heading_style = styles["Heading2"]
    heading_style.fontName = FONT_NAME
    heading_style.fontSize = 15

    subheading_style = styles["Heading3"]
    subheading_style.fontName = FONT_NAME

    normal_style = styles["BodyText"]
    normal_style.fontName = FONT_NAME
    normal_style.fontSize = 10
    normal_style.leading = 14

    pdf = SimpleDocTemplate(
        file_path,
        leftMargin=42,
        rightMargin=42,
        topMargin=36,
        bottomMargin=36,
    )

    story = []

    logo_path = os.path.join("static", "images", "logo.png")
    if os.path.exists(logo_path):
        try:
            with PILImage.open(logo_path) as logo_file:
                logo_file.verify()
            logo = Image(logo_path, width=52, height=52)
            brand = Paragraph("<b>TRAFFIC INTELLIGENCE</b><br/><font size=9 color='#64748B'>SAFETY &amp; OPERATIONS</font>", normal_style)
            brand_table = Table([[logo, brand]], colWidths=[65, 385])
            brand_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            story.append(brand_table)
            story.append(Spacer(1, 12))
        except Exception:
            pass

    story.append(Paragraph("Traffic Intelligence Executive Report", title_style))
    story.append(Paragraph("Prepared for operational review and leadership decision-making", normal_style))
    story.append(Spacer(1, 18))

    info_data = [
        [Paragraph("<b>Prepared By</b>", normal_style), Paragraph(str(username), normal_style)],
        [Paragraph("<b>Generated On</b>", normal_style), Paragraph(datetime.now().strftime("%d-%m-%Y %I:%M %p"), normal_style)],
        [Paragraph("<b>Report Type</b>", normal_style), Paragraph("Executive Traffic Safety Summary", normal_style)],
    ]
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("<b>Key Performance Indicators</b>", heading_style))
    kpi_rows = [["Metric", "Value"]]
    for key, value in kpis.items():
        kpi_rows.append([key.replace("_", " ").title(), str(value)])

    kpi_table = Table(kpi_rows, colWidths=[250, 200])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("<b>Executive Insights</b>", heading_style))
    for item in insights[:5]:
        story.append(Paragraph(f"• {item}", normal_style))
    story.append(Spacer(1, 18))

    story.append(Paragraph("<b>Recommended Actions</b>", heading_style))
    for item in recommendations[:5]:
        story.append(Paragraph(f"• {item}", normal_style))
    story.append(Spacer(1, 20))

    footer = Paragraph("Prepared by Traffic Intelligence Team • Confidential summary for business review", normal_style)
    story.append(footer)

    pdf.build(story, onFirstPage=_draw_page_chrome, onLaterPages=_draw_page_chrome)

    return file_path