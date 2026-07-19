from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
import os

def generate_thermal_receipt(invoice_data, paper_width_mm=80, output_path=None):
    """
    Generates a thermal POS receipt PDF for 80mm or 58mm printers.
    """
    if not output_path:
        inv_num = invoice_data.get('invoice_number', 'receipt').replace('/', '_')
        output_path = f"receipt_{inv_num}_{paper_width_mm}mm.pdf"

    width_pt = paper_width_mm * mm
    margin_pt = 3 * mm
    printable_width = width_pt - (2 * margin_pt)
    
    # Calculate dynamic height based on number of items
    items = invoice_data.get('items', [])
    base_height_mm = 160 if paper_width_mm == 80 else 180
    calculated_height_mm = base_height_mm + (len(items) * 12)
    height_pt = calculated_height_mm * mm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(width_pt, height_pt),
        leftMargin=margin_pt,
        rightMargin=margin_pt,
        topMargin=margin_pt,
        bottomMargin=margin_pt
    )

    styles = getSampleStyleSheet()
    font_size_base = 8 if paper_width_mm == 80 else 7
    font_size_title = 11 if paper_width_mm == 80 else 9

    title_style = ParagraphStyle(
        'ThermalTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=font_size_title,
        leading=font_size_title + 2,
        alignment=1, # Center
        textColor=colors.black
    )

    center_style = ParagraphStyle(
        'ThermalCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=font_size_base,
        leading=font_size_base + 2,
        alignment=1, # Center
        textColor=colors.black
    )

    normal_style = ParagraphStyle(
        'ThermalNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=font_size_base,
        leading=font_size_base + 2,
        textColor=colors.black
    )

    bold_style = ParagraphStyle(
        'ThermalBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=font_size_base,
        leading=font_size_base + 2,
        textColor=colors.black
    )

    right_bold = ParagraphStyle(
        'ThermalRightBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=font_size_base,
        leading=font_size_base + 2,
        alignment=2, # Right
        textColor=colors.black
    )

    elements = []

    # Header / Company Info
    company_name = invoice_data.get('company_name', 'My Shop')
    elements.append(Paragraph(f"<b>{company_name}</b>", title_style))
    
    if invoice_data.get('company_address'):
        addr = invoice_data['company_address'].replace('\n', ', ')
        elements.append(Paragraph(addr, center_style))
    
    contact_parts = []
    if invoice_data.get('company_phone'):
        contact_parts.append(f"Ph: {invoice_data['company_phone']}")
    if invoice_data.get('company_gstin'):
        contact_parts.append(f"GSTIN: {invoice_data['company_gstin']}")
    
    if contact_parts:
        elements.append(Paragraph(" | ".join(contact_parts), center_style))

    elements.append(Paragraph("-" * (42 if paper_width_mm == 80 else 32), center_style))

    # Receipt Info
    inv_num = invoice_data.get('invoice_number', 'N/A')
    date_str = str(invoice_data.get('date', ''))[:10]
    salesperson = invoice_data.get('salesperson', 'Cashier')
    cust_name = invoice_data.get('customer_name', 'Walk-in Customer')

    elements.append(Paragraph(f"Receipt #: <b>{inv_num}</b>", normal_style))
    elements.append(Paragraph(f"Date: {date_str}   Cashier: {salesperson}", normal_style))
    elements.append(Paragraph(f"Customer: {cust_name}", normal_style))

    elements.append(Paragraph("-" * (42 if paper_width_mm == 80 else 32), center_style))

    # Items Table
    table_data = []
    # Column headers
    if paper_width_mm == 80:
        table_data.append(["Item", "Qty", "Rate", "Amount"])
        col_widths = [printable_width * 0.45, printable_width * 0.15, printable_width * 0.20, printable_width * 0.20]
    else:
        table_data.append(["Item", "Qty", "Amt"])
        col_widths = [printable_width * 0.50, printable_width * 0.20, printable_width * 0.30]

    for item in items:
        name = item.get('name', 'Item')
        qty = item.get('quantity', 1)
        rate = item.get('rate', 0.0)
        amount = item.get('amount', qty * rate)
        
        # Trim name if needed
        if len(name) > 18:
            name = name[:16] + ".."
            
        if paper_width_mm == 80:
            table_data.append([
                Paragraph(name, normal_style),
                str(qty),
                f"{rate:.2f}",
                f"{amount:.2f}"
            ])
        else:
            table_data.append([
                Paragraph(name, normal_style),
                str(qty),
                f"{amount:.2f}"
            ])

    item_table = Table(table_data, colWidths=col_widths)
    item_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size_base),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
    ]))
    elements.append(item_table)

    elements.append(Paragraph("-" * (42 if paper_width_mm == 80 else 32), center_style))

    # Summary Totals
    subtotal = invoice_data.get('subtotal', 0.0)
    tax_amount = invoice_data.get('tax_amount', 0.0)
    discount = invoice_data.get('discount_amount', 0.0)
    grand_total = invoice_data.get('grand_total', 0.0)

    summary_data = [
        ["Subtotal:", f"{subtotal:.2f}"],
        ["Tax (GST):", f"{tax_amount:.2f}"],
        ["Discount:", f"-{discount:.2f}"],
        ["TOTAL:", f"INR {grand_total:.2f}"]
    ]

    summary_table = Table(summary_data, colWidths=[printable_width * 0.6, printable_width * 0.4])
    summary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size_base),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.black),
    ]))
    elements.append(summary_table)

    elements.append(Paragraph("=" * (42 if paper_width_mm == 80 else 32), center_style))

    # Footer
    elements.append(Paragraph("<b>Thank you for shopping with us!</b>", center_style))
    elements.append(Paragraph("Powered by LedgerPro POS v3.5.0", center_style))

    doc.build(elements)
    return output_path
