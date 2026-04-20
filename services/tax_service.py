from decimal import Decimal, ROUND_HALF_UP

class TaxService:
    def __init__(self):
        self.cgst_rate = 9
        self.sgst_rate = 9
        self.igst_rate = 18
    
    def calculate_tax(self, amount, tax_type='gst', cgst_rate=None, sgst_rate=None, igst_rate=None):
        """Calculate tax based on type"""
        amount = Decimal(str(amount))
        
        if tax_type == 'gst_intra_state':  # Within state - CGST + SGST
            cgst = amount * Decimal(str(cgst_rate or self.cgst_rate)) / 100
            sgst = amount * Decimal(str(sgst_rate or self.sgst_rate)) / 100
            return {
                'cgst': float(cgst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'sgst': float(sgst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'igst': 0,
                'total_tax': float((cgst + sgst).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            }
        else:  # Inter-state - IGST
            igst = amount * Decimal(str(igst_rate or self.igst_rate)) / 100
            return {
                'cgst': 0,
                'sgst': 0,
                'igst': float(igst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
                'total_tax': float(igst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            }
    
    def calculate_item_total(self, quantity, unit_price, cgst_rate, sgst_rate, igst_rate):
        """Calculate item total with tax"""
        quantity = Decimal(str(quantity))
        unit_price = Decimal(str(unit_price))
        subtotal = quantity * unit_price
        
        tax_result = self.calculate_tax(float(subtotal), 'gst_intra_state' if igst_rate == 0 else 'igst',
                                       cgst_rate, sgst_rate, igst_rate)
        
        total = subtotal + Decimal(str(tax_result['total_tax']))
        
        return {
            'subtotal': float(subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)),
            'cgst_amount': tax_result['cgst'],
            'sgst_amount': tax_result['sgst'],
            'igst_amount': tax_result['igst'],
            'total_tax': tax_result['total_tax'],
            'total': float(total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
        }
    
    def format_tax_breakdown(self, cgst, sgst, igst):
        """Format tax breakdown for display"""
        breakdown = []
        if cgst > 0:
            breakdown.append(f"CGST: ₹{cgst:.2f}")
        if sgst > 0:
            breakdown.append(f"SGST: ₹{sgst:.2f}")
        if igst > 0:
            breakdown.append(f"IGST: ₹{igst:.2f}")
        return " | ".join(breakdown)