from reportlab.lib import colors
from reportlab.platypus import (
    Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

from pdf.generator import get_unicode_font

# ─────────────────────────────────────────────────────────────────
# Font registration — Segoe UI has ₹ in BOTH regular and bold
# ─────────────────────────────────────────────────────────────────
_THERMAL_FONT_REG  = None
_THERMAL_FONT_BOLD = None

_FONT_CANDIDATES = [
    # (reg_name, reg_path, bold_name, bold_path)
    ('SegoeUI', r'C:\Windows\Fonts\segoeui.ttf',
     'SegoeUI-Bold', r'C:\Windows\Fonts\segoeuib.ttf'),
    ('ArialUnicode', r'C:\Windows\Fonts\ARIALUNI.ttf',
     'ArialUnicode', r'C:\Windows\Fonts\ARIALUNI.ttf'),  # no true bold — reuse regular
    ('NotoSans', r'C:\Windows\Fonts\NotoSans-Regular.ttf',
     'NotoSans-Bold', r'C:\Windows\Fonts\NotoSans-Bold.ttf'),
]


def _ensure_fonts():
    global _THERMAL_FONT_REG, _THERMAL_FONT_BOLD
    if _THERMAL_FONT_REG:
        return _THERMAL_FONT_REG, _THERMAL_FONT_BOLD
    for reg_name, reg_path, bold_name, bold_path in _FONT_CANDIDATES:
        if not os.path.exists(reg_path):
            continue
        try:
            pdfmetrics.registerFont(TTFont(reg_name, reg_path))
            if bold_name != reg_name and os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
            _THERMAL_FONT_REG  = reg_name
            _THERMAL_FONT_BOLD = bold_name
            return _THERMAL_FONT_REG, _THERMAL_FONT_BOLD
        except Exception as e:
            print(f'[thermal] Font registration failed ({reg_name}): {e}')
    _THERMAL_FONT_REG  = 'Helvetica'
    _THERMAL_FONT_BOLD = 'Helvetica-Bold'
    return _THERMAL_FONT_REG, _THERMAL_FONT_BOLD


def generate_thermal_receipt(invoice_data, paper_width_mm=80, output_path=None):
    """
    Professional 80mm / 58mm thermal POS receipt.

    Layout
    ──────
    THE SPACE LAB
    GSTIN: XXXX            Mob: XXXX
    Bill No.: XXX          Date: XXXX
    Add: Address line

    ─────────────────────────────
    sl.no   Qty      Rate   Amount
    ─────────────────────────────
    1. Full Item Name / Description
              11   ₹50.00  ₹649.00
    - - - - - - - - - - - - - - -
    2. Another Item
              11  ₹370.00 ₹4802.60
    - - - - - - - - - - - - - - -
    ─────────────────────────────
    Total    35  ₹241.65 ₹2997.00
    ─────────────────────────────
         GST Applicable : ₹539.46
                Payable : ₹3537.00
    ═════════════════════════════
    Thank You For Shopping With Us!
    """
    if not output_path:
        inv_num = invoice_data.get('invoice_number', 'receipt').replace('/', '_')
        output_path = f'receipt_{inv_num}_{paper_width_mm}mm.pdf'

    fr, fb = _ensure_fonts()   # fr = regular font, fb = bold font

    width_pt  = paper_width_mm * mm
    margin_pt = 3 * mm
    pw        = width_pt - 2 * margin_pt   # printable width

    items      = invoice_data.get('items', [])
    base_h     = 130 if paper_width_mm == 80 else 150
    page_h_pt  = (base_h + len(items) * 16) * mm

    doc = SimpleDocTemplate(
        output_path,
        pagesize=(width_pt, page_h_pt),
        leftMargin=margin_pt, rightMargin=margin_pt,
        topMargin=3 * mm,    bottomMargin=3 * mm,
    )

    # ── sizes ──────────────────────────────────────────────────────
    fs   = 8  if paper_width_mm == 80 else 7
    fs_t = 12 if paper_width_mm == 80 else 10
    fs_s = 7  if paper_width_mm == 80 else 6

    def ps(name, align=0, size=None, bold=False, color=colors.black):
        return ParagraphStyle(
            name,
            fontName=fb if bold else fr,
            fontSize=size or fs,
            leading=(size or fs) + 3,
            alignment=align,
            textColor=color,
            spaceAfter=0, spaceBefore=0,
        )

    sL   = ps('sL',  0)
    sC   = ps('sC',  1)
    sR   = ps('sR',  2)
    sLb  = ps('sLb', 0, bold=True)
    sRb  = ps('sRb', 2, bold=True)
    sCb  = ps('sCb', 1, bold=True)
    sT   = ps('sT',  1, fs_t, bold=True)
    sSm  = ps('sSm', 1, fs_s)

    def hr(thick=0.5, clr=colors.black):
        return HRFlowable(width=pw, thickness=thick, color=clr,
                          spaceAfter=1 * mm, spaceBefore=1 * mm)

    elems = []

    # ══════════════════════════════════════════════════════════════
    # HEADER
    # ══════════════════════════════════════════════════════════════
    company_name = (invoice_data.get('company_name') or 'My Shop').upper()
    elems.append(Paragraph(company_name, sT))
    elems.append(Spacer(1, 1.5 * mm))

    gst_val   = invoice_data.get('company_gstin') or invoice_data.get('outlet_gstin') or ''
    phone_val = invoice_data.get('company_phone') or invoice_data.get('outlet_phone') or ''
    if gst_val or phone_val:
        t = Table([[Paragraph(f'GSTIN: {gst_val}' if gst_val else '', sL),
                    Paragraph(f'Mob: {phone_val}'  if phone_val else '', sR)]],
                  colWidths=[pw * 0.55, pw * 0.45])
        t.setStyle(TableStyle([
            ('LEFTPADDING',   (0,0),(-1,-1), 0),
            ('RIGHTPADDING',  (0,0),(-1,-1), 0),
            ('TOPPADDING',    (0,0),(-1,-1), 0),
            ('BOTTOMPADDING', (0,0),(-1,-1), 1),
            ('VALIGN',        (0,0),(-1,-1), 'TOP'),
        ]))
        elems.append(t)

    inv_num  = invoice_data.get('invoice_number', 'N/A')
    date_str = str(invoice_data.get('date', ''))[:10]
    t2 = Table([[Paragraph(f'Bill No.: <b>{inv_num}</b>', sL),
                 Paragraph(f'Date: <b>{date_str}</b>',   sR)]],
               colWidths=[pw * 0.55, pw * 0.45])
    t2.setStyle(TableStyle([
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 0),
        ('BOTTOMPADDING', (0,0),(-1,-1), 1),
        ('VALIGN',        (0,0),(-1,-1), 'TOP'),
    ]))
    elems.append(t2)

    addr_val = invoice_data.get('company_address') or invoice_data.get('outlet_address') or ''
    if addr_val:
        elems.append(Paragraph('Add: ' + addr_val.replace('\n', ', '), sL))

    elems.append(hr())

    # ══════════════════════════════════════════════════════════════
    # COLUMN HEADERS  — all 4 on ONE row
    # sl.no | Qty | Rate | Amount
    # ══════════════════════════════════════════════════════════════
    # Column widths
    cw = [pw * 0.16,   # sl.no
          pw * 0.18,   # Qty
          pw * 0.31,   # Rate
          pw * 0.35]   # Amount

    hdr_row = [
        Paragraph('sl.no',  sLb),
        Paragraph('Qty',    sCb),
        Paragraph('Rate',   sRb),
        Paragraph('Amount', sRb),
    ]
    hdr_t = Table([hdr_row], colWidths=cw)
    hdr_t.setStyle(TableStyle([
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 1),
        ('BOTTOMPADDING', (0,0),(-1,-1), 2),
        ('LINEBELOW',     (0,0),(-1,-1), 0.5, colors.black),
    ]))
    elems.append(hdr_t)
    elems.append(Spacer(1, 0.5 * mm))

    # ══════════════════════════════════════════════════════════════
    # ITEM ROWS
    # ══════════════════════════════════════════════════════════════
    total_qty    = 0
    total_amount = 0.0
    INR = '\u20b9'   # ₹

    for idx, item in enumerate(items, start=1):
        name   = (item.get('name') or item.get('item_name') or 'Item').strip()
        qty    = item.get('quantity', 1)
        rate   = float(item.get('rate', 0.0))
        amount = float(item.get('amount', qty * rate))
        total_qty    += qty
        total_amount += amount

        # Line 1: idx. Full Item Name
        elems.append(Paragraph(f'<b>{idx}. {name}</b>', sL))

        # Line 2: values aligned under columns
        val_row = [
            Paragraph('', sL),
            Paragraph(str(int(qty)) if qty == int(qty) else str(qty), sC),
            Paragraph(f'{INR}{rate:.2f}',   sR),
            Paragraph(f'{INR}{amount:.2f}', sR),
        ]
        val_t = Table([val_row], colWidths=cw)
        val_t.setStyle(TableStyle([
            ('LEFTPADDING',   (0,0),(-1,-1), 0),
            ('RIGHTPADDING',  (0,0),(-1,-1), 0),
            ('TOPPADDING',    (0,0),(-1,-1), 1),
            ('BOTTOMPADDING', (0,0),(-1,-1), 2),
        ]))
        elems.append(val_t)

        # Thin separator between items
        elems.append(HRFlowable(width=pw, thickness=0.3,
                                color=colors.HexColor('#AAAAAA'),
                                spaceAfter=1 * mm, spaceBefore=1 * mm))

    # ══════════════════════════════════════════════════════════════
    # TOTALS
    # ══════════════════════════════════════════════════════════════
    subtotal    = float(invoice_data.get('subtotal', 0.0) or 0.0)
    tax_amount  = float(invoice_data.get('tax_amount', 0.0) or 0.0)
    grand_total = float(invoice_data.get('grand_total', 0.0) or 0.0)

    if subtotal == 0.0 and items:
        subtotal = sum(float(i.get('amount', i.get('quantity', 1) * i.get('rate', 0.0)))
                       for i in items)
    if grand_total == 0.0:
        grand_total = subtotal + tax_amount - float(invoice_data.get('discount_amount', 0.0))

    # Total row
    tot_row = [
        Paragraph('<b>Total</b>', sLb),
        Paragraph(f'<b>{int(total_qty) if total_qty == int(total_qty) else total_qty}</b>', sCb),
        Paragraph('', sR),
        Paragraph(f'<b>{INR}{subtotal:.2f}</b>', sRb),
    ]
    tot_t = Table([tot_row], colWidths=cw)
    tot_t.setStyle(TableStyle([
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,0),(-1,-1), 3),
        ('LINEBELOW',     (0,0),(-1,-1), 0.5, colors.black),
    ]))
    elems.append(tot_t)

    # GST Applicable
    gst_row = [
        Paragraph('GST Applicable :', sLb),
        Paragraph(f'{INR}{tax_amount:.2f}', sRb),
    ]
    gst_t = Table([gst_row], colWidths=[pw * 0.60, pw * 0.40])
    gst_t.setStyle(TableStyle([
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 2),
        ('BOTTOMPADDING', (0,0),(-1,-1), 2),
    ]))
    elems.append(gst_t)

    # Payable — bold, prominent double-bordered
    pay_row = [
        Paragraph('<b>Payable :</b>', sRb),
        Paragraph(f'<b>{INR}{grand_total:.2f}</b>', sRb),
    ]
    pay_t = Table([pay_row], colWidths=[pw * 0.50, pw * 0.50])
    pay_t.setStyle(TableStyle([
        ('LEFTPADDING',   (0,0),(-1,-1), 0),
        ('RIGHTPADDING',  (0,0),(-1,-1), 0),
        ('TOPPADDING',    (0,0),(-1,-1), 3),
        ('BOTTOMPADDING', (0,0),(-1,-1), 3),
        ('LINEABOVE',     (0,0),(-1,-1), 1.0, colors.black),
    ]))
    elems.append(pay_t)

    # ══════════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════════
    elems.append(Spacer(1, 2 * mm))
    elems.append(hr(0.4, colors.HexColor('#999999')))
    elems.append(Paragraph('Thank You For Shopping With Us!', sSm))
    elems.append(Paragraph('Powered by TSL SwiftBill ERP POS', sSm))

    doc.build(elems)
    return output_path
