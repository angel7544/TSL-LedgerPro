from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import json

UNICODE_FONT_NAME = None


def get_unicode_font():
    global UNICODE_FONT_NAME
    if UNICODE_FONT_NAME:
        return UNICODE_FONT_NAME
    font_candidates = [
        ("ArialUnicode", r"C:\Windows\Fonts\arial.ttf"),
        ("DejaVuSans", r"C:\Windows\Fonts\DejaVuSans.ttf"),
    ]
    for name, path in font_candidates:
        try:
            if os.path.exists(path):
                pdfmetrics.registerFont(TTFont(name, path))
                UNICODE_FONT_NAME = name
                return UNICODE_FONT_NAME
        except Exception as e:
            print(f"Error registering font {name}: {e}")
    UNICODE_FONT_NAME = "Helvetica"
    return UNICODE_FONT_NAME

def draw_header(c, data, title="INVOICE"):
    """Draws the header with logo and company details."""
    width, height = A4
    
    # Logo
    logo_path = data.get('logo_path')
    if logo_path and os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 30, height - 80, width=100, height=50, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            print(f"Error loading logo: {e}")
            
    # Company Details (Right aligned or Centered if desired, let's keep Left but below/beside logo)
    # Actually, standard is Logo Left, Company Name Right or Center.
    # Let's put Company Info on Top Left (under logo) or Top Right.
    # Current code had Company Name at 50, height-50.
    
    c.setFont("Helvetica-Bold", 20)
    c.drawRightString(width - 30, height - 50, title)
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30, height - 100, data.get('company_name', 'Company Name'))
    
    c.setFont("Helvetica", 10)
    y = height - 115
    if data.get('company_address'):
        addr_lines = data.get('company_address', '').split('\n')
        for line in addr_lines:
            c.drawString(30, y, line)
            y -= 12
    
    contact_info = []
    if data.get('company_email'): contact_info.append(f"Email: {data['company_email']}")
    if data.get('company_phone'): contact_info.append(f"Ph: {data['company_phone']}")
    if data.get('company_website'): contact_info.append(f"Web: {data['company_website']}")
    
    if contact_info:
        c.drawString(30, y, " | ".join(contact_info))
        y -= 12
        
    if data.get('company_gstin'):
        c.drawString(30, y, f"GSTIN: {data['company_gstin']}")
        y -= 12
        
    # Divider
    c.setLineWidth(1)
    c.line(30, y - 5, width - 30, y - 5)
    
    return y - 20

def draw_status_badge(c, status, x, y):
    """Draws a status badge (Paid, Due, etc.) at (x, y) - top right corner of badge."""
    if not status:
        return
        
    status = status.upper()
    c.saveState()
    
    # Colors
    if status in ['PAID', 'RECEIVED']:
        bg_color = colors.Color(0.1, 0.7, 0.1) # Green
        text_color = colors.white
    elif status in ['PARTIAL', 'PARTIALLY PAID']:
        bg_color = colors.Color(1.0, 0.6, 0.0) # Orange
        text_color = colors.white
    elif status in ['DUE', 'UNPAID']:
        bg_color = colors.Color(0.8, 0.2, 0.2) # Red
        text_color = colors.white
    elif status == 'DRAFT':
        bg_color = colors.Color(0.5, 0.5, 0.5) # Grey
        text_color = colors.white
    else:
        bg_color = colors.Color(0.9, 0.9, 0.9) # Light Grey
        text_color = colors.black
        
    # Draw Badge
    width = 80
    height = 25
    c.setFillColor(bg_color)
    # Round rect: x, y, width, height, radius
    # ReportLab rect draws from bottom-left. 
    # If (x, y) is top-right, then bottom-left is (x - width, y - height)
    c.roundRect(x - width, y - height, width, height, 6, fill=1, stroke=0)
    
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(x - width/2, y - height + 8, status)
    
    c.restoreState()

def generate_invoice_pdf(invoice_data, filename="invoice.pdf"):
    """
    Generates a PDF invoice with enhanced details.
    """
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    y = draw_header(c, invoice_data, "INVOICE")
    
    # Status Badge
    draw_status_badge(c, invoice_data.get('status', ''), width - 30, y + 30)
    
    # Invoice Details (Right Side)
    c.setFont("Helvetica-Bold", 10)
    right_x = width - 200
    c.drawString(right_x, y, "Invoice Details")
    c.setFont("Helvetica", 10)
    c.drawString(right_x, y - 15, f"Invoice #: {invoice_data.get('invoice_number', '')}")
    c.drawString(right_x, y - 30, f"Date: {invoice_data.get('date', '')}")
    if invoice_data.get('due_date'):
        c.drawString(right_x, y - 45, f"Due Date: {invoice_data.get('due_date', '')}")
    if invoice_data.get('order_number'):
        c.drawString(right_x, y - 60, f"Order #: {invoice_data.get('order_number', '')}")
    if invoice_data.get('payment_terms'):
        c.drawString(right_x, y - 75, f"Terms: {invoice_data.get('payment_terms', '')}")
        
    # Bill To (Left Side)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Bill To:")
    c.setFont("Helvetica", 10)
    c.drawString(30, y - 15, invoice_data.get('customer_name', ''))
    
    # Handle multi-line address
    addr = invoice_data.get('customer_address', '') or ''
    addr_lines = addr.split('\n')
    ay = y - 30
    for line in addr_lines[:3]: # Limit lines
        c.drawString(30, ay, line)
        ay -= 12
        
    if invoice_data.get('customer_gstin'):
        c.drawString(30, ay, f"GSTIN: {invoice_data['customer_gstin']}")
        
    # Table Start Position
    table_y = y - 100
    
    # Items Table
    data = [["Item", "Qty", "Rate", "Disc %", "GST %", "Amount"]]
    
    for item in invoice_data.get('items', []):
        name = item.get('name', 'Unknown')
        qty = str(item.get('quantity', 0))
        rate = f"{item.get('rate', 0):.2f}"
        disc = f"{item.get('discount_percent', 0)}%"
        gst = f"{item.get('gst_percent', 0)}%"
        amt = f"{item.get('amount', 0):.2f}"
        
        data.append([name, qty, rate, disc, gst, amt])
        
    # Column Widths
    col_widths = [220, 50, 70, 50, 50, 90]
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'), # Align items left
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    table.wrapOn(c, width, height)
    # Calculate height of table
    table_height = len(data) * 20 # Approx
    
    # Check if table fits
    if table_y - table_height < 100:
        # If table is too long, we might need new page logic, but for now just let it run or clip
        # Real impl would handle pagination
        pass
        
    table.drawOn(c, 30, table_y - table_height)
    
    # Totals Section
    total_y = table_y - table_height - 20
    
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 30, total_y, f"Subtotal: {invoice_data.get('subtotal', 0):.2f}")
    total_y -= 15
    c.drawRightString(width - 30, total_y, f"Tax: {invoice_data.get('tax_amount', 0):.2f}")
    total_y -= 15
    
    if invoice_data.get('discount_amount'):
        c.drawRightString(width - 30, total_y, f"Discount: -{invoice_data.get('discount_amount', 0):.2f}")
        total_y -= 15
        
    if invoice_data.get('tds_amount'):
        c.drawRightString(width - 30, total_y, f"TDS: -{invoice_data.get('tds_amount', 0):.2f}")
        total_y -= 15
        
    if invoice_data.get('tcs_amount'):
        c.drawRightString(width - 30, total_y, f"TCS: +{invoice_data.get('tcs_amount', 0):.2f}")
        total_y -= 15
        
    if invoice_data.get('adjustment'):
        c.drawRightString(width - 30, total_y, f"Adjustment: {invoice_data.get('adjustment', 0):.2f}")
        total_y -= 15
        
    if invoice_data.get('round_off'):
        c.drawRightString(width - 30, total_y, f"Round Off: {invoice_data.get('round_off', 0):.2f}")
        total_y -= 15
        
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 30, total_y - 5, f"Grand Total: {invoice_data.get('grand_total', 0):.2f}")
    
    # Notes & Terms (Left Side)
    notes_y = table_y - table_height - 20
    c.setFont("Helvetica-Bold", 10)
    
    if invoice_data.get('customer_notes'):
        c.drawString(30, notes_y, "Notes:")
        c.setFont("Helvetica", 9)
        # Wrap text if needed (simple implementation)
        c.drawString(30, notes_y - 12, str(invoice_data['customer_notes'])[:80]) 
        notes_y -= 30
        
    c.setFont("Helvetica-Bold", 10)
    if invoice_data.get('terms_conditions'):
        c.drawString(30, notes_y, "Terms & Conditions:")
        c.setFont("Helvetica", 9)
        c.drawString(30, notes_y - 12, str(invoice_data['terms_conditions'])[:80])
        notes_y -= 30

    # Custom Fields
    if invoice_data.get('custom_fields'):
        try:
            custom_fields = json.loads(invoice_data['custom_fields'])
            if custom_fields:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(30, notes_y, "Additional Information:")
                c.setFont("Helvetica", 9)
                notes_y -= 12
                for key, value in custom_fields.items():
                    c.drawString(30, notes_y, f"{key}: {value}")
                    notes_y -= 12
        except:
            pass
        
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 30, "Generated by BR31-Technologies_LedgerPro")
    
    c.save()

def generate_bill_pdf(bill_data, filename="bill.pdf"):
    """Generates a PDF for Purchase Bill."""
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    y = draw_header(c, bill_data, "PURCHASE BILL")
    
    # Status Badge
    draw_status_badge(c, bill_data.get('status', ''), width - 30, y + 30)
    
    # Bill Details
    c.setFont("Helvetica-Bold", 10)
    right_x = width - 200
    c.drawString(right_x, y, "Bill Details")
    c.setFont("Helvetica", 10)
    c.drawString(right_x, y - 15, f"Bill #: {bill_data.get('bill_number', '')}")
    c.drawString(right_x, y - 30, f"Date: {bill_data.get('date', '')}")
    
    current_y = y - 45
    if bill_data.get('due_date'):
        c.drawString(right_x, current_y, f"Due Date: {bill_data.get('due_date', '')}")
        current_y -= 15
    if bill_data.get('order_number'):
        c.drawString(right_x, current_y, f"Order #: {bill_data.get('order_number', '')}")
        current_y -= 15
    if bill_data.get('payment_terms'):
        c.drawString(right_x, current_y, f"Terms: {bill_data.get('payment_terms', '')}")
        current_y -= 15
    if bill_data.get('reverse_charge'):
        c.drawString(right_x, current_y, "Reverse Charge: Yes")
        current_y -= 15
        
    # Vendor Details
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Vendor:")
    c.setFont("Helvetica", 10)
    c.drawString(30, y - 15, bill_data.get('vendor_name', ''))
    
    # Handle multi-line address
    addr = bill_data.get('vendor_address', '') or ''
    addr_lines = addr.split('\n')
    ay = y - 30
    for line in addr_lines[:3]: # Limit lines
        c.drawString(30, ay, line)
        ay -= 12
        
    if bill_data.get('vendor_gstin'):
        c.drawString(30, ay, f"GSTIN: {bill_data['vendor_gstin']}")
    
    # Table
    table_y = y - 100
    data = [["Item", "Qty", "Rate", "GST %", "Amount"]]
    
    for item in bill_data.get('items', []):
        name = item.get('name') or item.get('item_name', 'Unknown')
        data.append([
            name,
            str(item.get('quantity', 0)),
            f"{item.get('rate', 0):.2f}",
            f"{item.get('gst_percent', 0)}%",
            f"{item.get('amount', 0):.2f}"
        ])
        
    col_widths = [250, 60, 80, 60, 90]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    table.wrapOn(c, width, height)
    table_height = len(data) * 20
    table.drawOn(c, 30, table_y - table_height)
    
    # Totals
    total_y = table_y - table_height - 20
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 30, total_y, f"Subtotal: {bill_data.get('subtotal', 0):.2f}")
    total_y -= 15
    c.drawRightString(width - 30, total_y, f"Tax: {bill_data.get('tax_amount', 0):.2f}")
    total_y -= 15
    
    if bill_data.get('discount_amount'):
        c.drawRightString(width - 30, total_y, f"Discount: -{bill_data.get('discount_amount', 0):.2f}")
        total_y -= 15
    
    if bill_data.get('tds_amount'):
        c.drawRightString(width - 30, total_y, f"TDS: -{bill_data.get('tds_amount', 0):.2f}")
        total_y -= 15
        
    if bill_data.get('tcs_amount'):
        c.drawRightString(width - 30, total_y, f"TCS: +{bill_data.get('tcs_amount', 0):.2f}")
        total_y -= 15
        
    if bill_data.get('adjustment'):
        c.drawRightString(width - 30, total_y, f"Adjustment: {bill_data.get('adjustment', 0):.2f}")
        total_y -= 15
        
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 30, total_y - 5, f"Grand Total: {bill_data.get('grand_total', 0):.2f}")
    
    # Notes - Removed as per user request (Internal use only)
    # if bill_data.get('notes'):
    #    notes_y = table_y - table_height - 20
    #    c.setFont("Helvetica-Bold", 10)
    #    c.drawString(30, notes_y, "Notes:")
    #    c.setFont("Helvetica", 9)
    #    c.drawString(30, notes_y - 12, str(bill_data['notes'])[:80])
    #    notes_y -= 30
    # else:
    notes_y = table_y - table_height - 20

    # Custom Fields
    if bill_data.get('custom_fields'):
        try:
            custom_fields = json.loads(bill_data['custom_fields'])
            if custom_fields:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(30, notes_y, "Additional Information:")
                c.setFont("Helvetica", 9)
                notes_y -= 12
                for key, value in custom_fields.items():
                    c.drawString(30, notes_y, f"{key}: {value}")
                    notes_y -= 12
        except:
            pass

    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 30, "Generated by LedgerPro")
    
    c.save()

def generate_payment_receipt_pdf(payment_data, filename="receipt.pdf"):
    """Generates a PDF Receipt for Payment Received."""
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    y = draw_header(c, payment_data, "PAYMENT RECEIPT")
    
    # Receipt Details
    c.setFont("Helvetica-Bold", 10)
    right_x = width - 200
    c.drawString(right_x, y, "Receipt Details")
    c.setFont("Helvetica", 10)
    c.drawString(right_x, y - 15, f"Payment #: {payment_data.get('payment_number', '')}")
    c.drawString(right_x, y - 30, f"Date: {payment_data.get('date', '')}")
    c.drawString(right_x, y - 45, f"Method: {payment_data.get('method', '')}")
    if payment_data.get('reference'):
        c.drawString(right_x, y - 60, f"Ref #: {payment_data.get('reference', '')}")
        
    # Received From
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, y, "Received From:")
    c.setFont("Helvetica", 10)
    c.drawString(30, y - 15, payment_data.get('customer_name', ''))
    
    # Amount Received Big
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, y - 100, f"Amount Received: {payment_data.get('amount_received', 0):.2f}")
    
    # Applied Invoices Table
    table_y = y - 140
    c.setFont("Helvetica-Bold", 10)
    c.drawString(30, table_y + 10, "Payment Allocation:")
    
    data = [["Invoice Date", "Invoice #", "Invoice Amount", "Payment Amount"]]
    
    for alloc in payment_data.get('allocations', []):
        data.append([
            alloc.get('date', ''),
            alloc.get('invoice_number', ''),
            f"{alloc.get('invoice_total', 0):.2f}",
            f"{alloc.get('amount', 0):.2f}"
        ])
        
    col_widths = [100, 100, 100, 120]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    
    table.wrapOn(c, width, height)
    table_height = len(data) * 20
    table.drawOn(c, 30, table_y - table_height)
    
    # Notes - Removed as per user request (Internal use only)
    # notes_y = table_y - table_height - 30
    # if payment_data.get('notes'):
    #    c.setFont("Helvetica-Bold", 10)
    #    c.drawString(30, notes_y, "Notes:")
    #    c.setFont("Helvetica", 9)
    #    c.drawString(30, notes_y - 12, str(payment_data['notes'])[:80])
    #    notes_y -= 30
    
    notes_y = table_y - table_height - 30
        
    # Thank You Note
    if payment_data.get('send_thank_you'):
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width/2, notes_y - 20, "Thank you for your payment!")
        notes_y -= 40

    # Custom Fields
    if payment_data.get('custom_fields'):
        try:
            custom_fields = json.loads(payment_data['custom_fields'])
            if custom_fields:
                c.setFont("Helvetica-Bold", 10)
                c.drawString(30, notes_y, "Additional Information:")
                c.setFont("Helvetica", 9)
                notes_y -= 12
                for key, value in custom_fields.items():
                    c.drawString(30, notes_y, f"{key}: {value}")
                    notes_y -= 12
        except:
            pass
        
    # Footer
    c.setFont("Helvetica", 8)
    c.drawCentredString(width/2, 30, "Generated by LedgerPro")
    
    c.save()

def generate_price_list_pdf(items, filename="price_list.pdf"):
    """
    Generates a PDF price list (rates).
    items: list of dicts with name, sku, selling_price
    """
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("Price List / Rates", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Table Data
    data = [["Item Name", "SKU", "Price (INR)"]]
    for item in items:
        data.append([
            item.get('name', ''),
            item.get('sku', '') or '',
            f"{item.get('selling_price', 0):.2f}"
        ])
        
    # Table Style
    table = Table(data, colWidths=[300, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.whitesmoke, colors.lightgrey])
    ]))
    
    elements.append(table)
    doc.build(elements)

def generate_generic_report_pdf(report_data, headers, rows, filename="report.pdf", title="REPORT"):
    """
    Generates a generic PDF report with company header and a table.
    Uses SimpleDocTemplate for multi-page support.
    """
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=200, bottomMargin=50)
    width, height = A4

    # Optional: compute stock totals for Stock Valuation report
    stock_total_qty = None
    stock_total_value = None
    if title.upper() == "STOCK VALUATION" and len(headers) >= 5:
        try:
            qty_idx = 2
            val_idx = 4
            total_qty = 0.0
            total_val = 0.0
            for r in rows:
                if len(r) <= val_idx:
                    continue
                qty_str = (r[qty_idx] or "").replace("₹", "").replace(",", "").strip()
                val_str = (r[val_idx] or "").replace("₹", "").replace(",", "").strip()
                if qty_str:
                    total_qty += float(qty_str)
                if val_str:
                    total_val += float(val_str)
            stock_total_qty = total_qty
            stock_total_value = total_val
        except Exception:
            stock_total_qty = None
            stock_total_value = None

    # Avoid mutating caller's dict
    report_meta = dict(report_data)
    if stock_total_qty is not None and stock_total_value is not None:
        report_meta["stock_total_qty"] = stock_total_qty
        report_meta["stock_total_value"] = stock_total_value
    
    def draw_page_header(canvas, doc):
        canvas.saveState()
        y = draw_header(canvas, report_meta, title)
        font_name = get_unicode_font()
        canvas.setFont(font_name, 10)
        info_y = y
        canvas.drawString(30, info_y, f"Generated on: {report_meta.get('generated_date', '')}")
        if report_meta.get('date_range'):
            canvas.drawRightString(width - 30, info_y, f"Period: {report_meta.get('date_range', '')}")
        info_y -= 14
        if "stock_total_qty" in report_meta and "stock_total_value" in report_meta:
            canvas.setFont(font_name, 9)
            canvas.drawString(30, info_y, f"Total Stock Qty: {report_meta['stock_total_qty']:.2f}")
            canvas.drawRightString(width - 30, info_y, f"Total Stock Value: ₹{report_meta['stock_total_value']:.2f}")
        canvas.setFont(font_name, 8)
        canvas.drawRightString(width - 30, 30, f"Page {doc.page}")
        canvas.restoreState()

    elements = []
    
    data = [headers] + rows

    if stock_total_qty is not None and stock_total_value is not None:
        data.append([
            "TOTAL",
            "",
            f"{stock_total_qty:.2f}",
            "",
            f"₹{stock_total_value:.2f}"
        ])
    
    available_width = width - 60 # 30 left, 30 right margin
    col_count = len(headers)
    col_width = available_width / col_count
    col_widths = [col_width] * col_count
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    body_font = get_unicode_font()
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), body_font),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]

    if stock_total_qty is not None and stock_total_value is not None:
        last_row = len(data) - 1
        style_commands.append(('FONTNAME', (0, last_row), (-1, last_row), 'Helvetica-Bold'))
        style_commands.append(('BACKGROUND', (0, last_row), (-1, last_row), colors.Color(0.95, 0.95, 0.95)))

    table.setStyle(TableStyle(style_commands))
    
    elements.append(table)
    
    try:
        doc.build(elements, onFirstPage=draw_page_header, onLaterPages=draw_page_header)
    except Exception as e:
        print(f"Error building PDF: {e}")
