from accounts.pdf_utils import generate_official_pdf

def generate_funding_award_pdf(app):
    subject = "OFFICIAL NOTIFICATION OF FUNDING APPROVAL"
    
    details_dict = {
        "Funding Scheme": app.funding.title,
        "Approved Amount": f"INR {app.amount_requested}",
        "Interest Rate": f"{app.funding.interest_rate}% p.a.",
        "Purpose/Utilization": app.purpose,
        "Wallet Status": "ADDED (Available for Use)",
        "Tender Title": app.tender.title,
        "Tender ID": app.tender.tender_id,
        "Total Tender Value": f"INR {app.tender.estimated_value}",
    }
    
    acknowledgement_text = [
        f"This document is an official acknowledgement from the eBharat Financial Assistance Division that your funding application under the scheme '{app.funding.title}' has been thoroughly reviewed and officially approved.",
        f"The stated amount of INR {app.amount_requested} has been successfully credited to your eBharat Funding Wallet.",
        "Important Guideline: The allocated funds must strictly be applied toward the execution of the specified tender project. Failure to adhere to the terms and conditions outlined in the scheme guidelines may result in immediate revocation of the awarded funds."
    ]
    
    pdf_bytes = generate_official_pdf(subject,acknowledgement_text,details_dict,)
    return pdf_bytes

def generate_funding_application_pdf(app):
    subject = "OFFICIAL ACKNOWLEDGEMENT OF FUNDING APPLICATION"
    
    details_dict = {
        "Date of Submission": app.applied_at.strftime("%d %b %Y, %H:%M") if app.applied_at else "",
        "Funding Scheme": app.funding.title,
        "Requested Amount": f"INR {app.amount_requested}",
        "Purpose/Utilization": app.purpose,
        "Status": "PENDING REVIEW",
        "Tender Title": app.tender.title,
        "Tender ID": app.tender.tender_id,
        "Applicant": app.bidder.get_full_name() or app.bidder.username,
        "Email Address": app.bidder.email
    }
    
    acknowledgement_text = [
        f"This document is an official acknowledgement from the eBharat Financial Assistance Division that your funding application under the scheme '{app.funding.title}' has been successfully received by our portal.",
        f"Your application for an amount of INR {app.amount_requested} is currently pending review by the respective financial committee.",
        "Important Guideline: Please note that this is solely an acknowledgement of receipt and does not guarantee the approval of your funding application. You will be actively notified regarding any subsequent changes in your application status."
    ]
    
    pdf_bytes = generate_official_pdf(subject,acknowledgement_text,details_dict)
    return pdf_bytes
