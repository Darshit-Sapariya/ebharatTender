import razorpay
from django.conf import settings
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from accounts.utils import send_ebharat_email, send_email_in_background
from .models import TenderApplication
import logging

logger = logging.getLogger(__name__)

def award_bid_service(bid, request):
    """
    Business logic for awarding a bid:
    1. Mark bid as awarded.
    2. Auto-reject and refund other bidders.
    3. Update tender status.
    4. Send award notification and email with PDF.
    """
    from tenders.utils import generate_award_pdf  # Avoid circular import
    
    bid.status = "awarded"
    
    # Auto-reject and refund all other bids for this tender
    losing_bids = TenderApplication.objects.filter(tender=bid.tender).exclude(id=bid.id)
    for l_bid in losing_bids:
        l_bid.status = "rejected"
        if l_bid.payment_status == 'paid' and l_bid.razorpay_payment_id:
            try:
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                client.payment.refund(l_bid.razorpay_payment_id, {
                    "amount": int(l_bid.tender.emd_amount * 100)
                })
                l_bid.payment_status = "refunded"
            except Exception as e:
                logger.error(f"Refund failed for application {l_bid.id}: {e}")
        l_bid.save()
    
    # Close/Award the tender
    bid.tender.status = "awarded"
    bid.tender.save()
    
    # Send Official Award Email to Winner
    try:
        current_site = get_current_site(request)
        context = {
            "bidder_name": bid.applicant.first_name or bid.applicant.username,
            "company_name": bid.company_name,
            "tender_title": bid.tender.title,
            "tender_id": bid.tender.tender_id,
            "department": bid.tender.department,
            "location": bid.tender.location,
            "bid_amount": bid.bid_amount,
            "award_date": timezone.now().strftime("%d %B %Y"),
            "gst_number": bid.gst_number,
            "address": bid.registered_address,
            "domain": current_site.domain,
        }
        
        pdf_content = generate_award_pdf(context)
        attachments = [{
            'filename': f"Award_Letter_{bid.tender.tender_id}.pdf",
            'content': pdf_content,
            'mimetype': 'application/pdf'
        }]
        
        send_email_in_background(
            subject="Congratulations! Tender Awarded",
            template_name="bid_awarded.html",
            context=context,
            recipient_list=[bid.applicant.email],
            attachments=attachments
        )
    except Exception as e:
        logger.error(f"Award Email failed: {e}")
    
    bid.save()
    return True
