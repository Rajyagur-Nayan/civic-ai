import os
import time
from datetime import datetime
from typing import List, Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.units import inch
import logging

logger = logging.getLogger(__name__)

# Constants for file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_pothole_report(
    total_potholes: int,
    total_cost: float,
    severity_distribution: Dict[str, int],
    detections: List[Dict[str, Any]],
    sample_images: List[str] = None
) -> str:
    """
    Generate a professional PDF report for pothole detection results.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"report_{timestamp}.pdf"
    report_path = os.path.join(OUTPUT_DIR, report_filename)
    
    doc = SimpleDocTemplate(report_path, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#1A237E"),
        alignment=1, # Center
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'SubHeading',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor("#303F9F"),
        spaceBefore=12,
        spaceAfter=10
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("Road Damage Analysis Report", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))
    
    # 1. Summary Statistics
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_data = [
        ["Metric", "Value"],
        ["Total Potholes Detected", str(total_potholes)],
        ["Estimated Total Repair Cost", f"${total_cost:,.2f}"],
        ["Small Potholes", str(severity_distribution.get("small", 0))],
        ["Medium Potholes", str(severity_distribution.get("medium", 0))],
        ["Large Potholes", str(severity_distribution.get("large", 0))]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5 * inch, 2.5 * inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#3F51B5")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3 * inch))
    
    # 2. Detailed Detections Table
    elements.append(Paragraph("Detailed Detection Log", heading_style))
    
    log_data = [["ID", "Severity", "Area (m2)", "Cost ($)", "Conf (%)"]]
    for i, det in enumerate(detections[:50]): # Limit table to top 50
        log_data.append([
            f"#{i+1}",
            det.get("severity", "N/A").capitalize(),
            f"{det.get('area', 0):.2f}",
            f"{det.get('cost', 0):.2f}",
            f"{det.get('confidence', 0)*100:.1f}%"
        ])
    
    log_table = Table(log_data, colWidths=[0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#7986CB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(log_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # 3. Visual Evidence Gallery
    if sample_images:
        elements.append(Paragraph("Visual Evidence Gallery", heading_style))
        for img_path in sample_images:
            if os.path.exists(img_path):
                try:
                    # Resize image proportionally to fit width
                    img = RLImage(img_path, width=5.5 * inch, height=3.5 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.2 * inch))
                except Exception as e:
                    logger.error(f"Error adding image to PDF: {e}")
    
    # Build PDF
    try:
        doc.build(elements)
        logger.info(f"PDF Report generated successfully at: {report_path}")
        return report_path
    except Exception as e:
        logger.error(f"Failed to build PDF: {e}")
        return ""

def get_report_url(file_path: str) -> str:
    """Helper to convert absolute path to relative URL for frontend"""
    if not file_path: return ""
    return f"/reports/{os.path.basename(file_path)}"
