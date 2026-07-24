from accounts.pdf_utils import generate_official_pdf

def generate_award_pdf(context):
    subject = "OFFICIAL LETTER OF AWARD"
    
    details_dict = {
        "Reference ID": context.get('tender_id', 'N/A'),
        "Tender Title": context.get('tender_title', 'N/A'),
        "Department": context.get('department', 'N/A'),
        "Location": context.get('location', 'N/A'),
        "Awarded Amount": f"INR {context.get('bid_amount', '0.00')}",
        "Award Date": context.get('award_date', 'N/A'),
        "Company Name": context.get('company_name', 'N/A'),
        "GST Identification": context.get('gst_number', 'N/A'),
        "Registered Address": context.get('address', 'N/A'),
    }
    
    acknowledgement_text = [
        f"Dear {context.get('bidder_name', 'Authorized Representative')},",
        f"On behalf of the eBharat Government Tender Authority, we are honored to officially inform you that {context.get('company_name', 'your company')} has been successfully evaluated and awarded the contract for the tender detailed below.",
        "This decision was based on technical and financial clearance. The nodal procurement officer will contact you shortly regarding the formal contract signing, submission of the Performance Bank Guarantee (PBG), and project kickoff schedule. Please ensure all original physical copies of your documentation are ready for final verification."
    ]
    
    pdf_bytes = generate_official_pdf(subject, acknowledgement_text, details_dict)
    return pdf_bytes
