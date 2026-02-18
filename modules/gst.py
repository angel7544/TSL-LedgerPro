def calculate_gst(taxable_amount, gst_rate, seller_state, buyer_state, tax_inclusive=False):
    """
    Calculates GST components based on intra-state or inter-state transaction.
    
    Args:
        taxable_amount (float): The amount to calculate tax on.
        gst_rate (float): The GST rate in percentage (e.g., 18.0).
        seller_state (str): State of the seller.
        buyer_state (str): State of the buyer.
        tax_inclusive (bool): Whether the taxable_amount includes tax.
        
    Returns:
        dict: A dictionary containing breakdown of CGST, SGST, IGST, total tax, and grand total.
    """
    cgst_rate = 0.0
    sgst_rate = 0.0
    igst_rate = 0.0
    cgst_amount = 0.0
    sgst_amount = 0.0
    igst_amount = 0.0
    total_tax = 0.0
    grand_total = 0.0
    base_amount = 0.0

    is_intra_state = (seller_state.strip().lower() == buyer_state.strip().lower())

    if is_intra_state:
        cgst_rate = gst_rate / 2
        sgst_rate = gst_rate / 2
    else:
        igst_rate = gst_rate

    if tax_inclusive:
        # Formula: Tax = (Inclusive Amount * Rate) / (100 + Rate)
        # Base Amount = Inclusive Amount - Tax
        base_amount = (taxable_amount * 100) / (100 + gst_rate)
        total_tax = taxable_amount - base_amount
    else:
        base_amount = taxable_amount
        total_tax = (taxable_amount * gst_rate) / 100

    if is_intra_state:
        cgst_amount = total_tax / 2
        sgst_amount = total_tax / 2
    else:
        igst_amount = total_tax

    grand_total = base_amount + total_tax

    return {
        "base_amount": round(base_amount, 2),
        "cgst_rate": cgst_rate,
        "sgst_rate": sgst_rate,
        "igst_rate": igst_rate,
        "cgst_amount": round(cgst_amount, 2),
        "sgst_amount": round(sgst_amount, 2),
        "igst_amount": round(igst_amount, 2),
        "total_tax": round(total_tax, 2),
        "grand_total": round(grand_total, 2)
    }
