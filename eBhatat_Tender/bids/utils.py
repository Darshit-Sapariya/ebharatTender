from django.http import HttpResponse
from accounts.pdf_utils import generate_official_pdf

def generate_bid_receipt_pdf(bid):
    """
    Generates a premium, officially formatted PDF receipt for a submitted bid.
    """
    subject = "BID SUBMISSION ACKNOWLEDGEMENT"
    
    details_dict = {
        "Tender Title": bid.tender.title,
        "Tender Category": str(bid.tender.category),
        "Issuing Authority": str(bid.tender.created_by),
        "Estimated Tender Value": f"₹ {bid.tender.estimated_value}",
        "Company Name": bid.company_name,
        "GST Identification": bid.gst_number,
        "Authorized Representative": f"{bid.bidder_name} ({bid.designation})",
        "Submitted Bid Amount": f"₹ {bid.bid_amount}",
        "Application Date": bid.applied_at.strftime("%d %B %Y, %I:%M %p"),
        "Status": "RECEIVED & UNDER EVALUATION"
    }
    
    acknowledgement_text = [
        f"This system-generated document serves as the official acknowledgement that the bid submitted by {bid.company_name} for the tender '{bid.tender.title}' has been successfully received by the eBharat Procurement Portal.",
        "Your submission will be evaluated as per the technical and financial parameters outlined in the tender document. Please retain this receipt for your records and track further updates directly through your bidding dashboard."
    ]
    
    pdf_bytes = generate_official_pdf(subject, acknowledgement_text, details_dict)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="eBharat_Bid_Receipt_{bid.id}.pdf"'
    
    return response
