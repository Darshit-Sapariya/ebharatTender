import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

def send_ebharat_email(subject, template_name, context, recipient_list, attachments=None):
    """
    Sends a high-quality HTML email using a template.
    Completely fail-safe: catches all exceptions so email failures never crash the application.
    """
    try:
        # 1. Sanitize recipient list
        if not recipient_list:
            logger.warning("send_ebharat_email called with empty recipient_list")
            return False
            
        clean_recipients = [str(r).strip() for r in recipient_list if r and isinstance(r, str) and r.strip()]
        if not clean_recipients:
            logger.warning("send_ebharat_email: No valid recipient email addresses found")
            return False

        # 2. Get safe from_email
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None) or 'ebharattender@gmail.com'

        # 3. Render HTML content safely
        try:
            template_path = f'emails/{template_name}' if not template_name.startswith('emails/') else template_name
            html_content = render_to_string(template_path, context or {})
        except Exception as te:
            logger.error(f"Template rendering error for {template_name}: {te}")
            html_content = f"<h2>{subject}</h2><p>Please check your account portal for details.</p>"

        # 4. Strip tags for plain text
        text_content = strip_tags(html_content)

        # 5. Build email object
        email = EmailMultiAlternatives(
            subject=f"{subject} | eBharat Tender",
            body=text_content,
            from_email=from_email,
            to=clean_recipients
        )

        email.attach_alternative(html_content, "text/html")

        # 6. Attach any files safely
        if attachments:
            for attachment in attachments:
                try:
                    if isinstance(attachment, dict) and 'filename' in attachment and 'content' in attachment:
                        email.attach(
                            attachment['filename'],
                            attachment['content'],
                            attachment.get('mimetype', 'application/pdf')
                        )
                except Exception as ae:
                    logger.error(f"Attachment error in email for {subject}: {ae}")

        # 7. Send email safely with fail_silently=False wrapped in exception handler
        sent_count = email.send(fail_silently=False)
        return bool(sent_count)

    except Exception as e:
        logger.error(f"SMTP / Email dispatch error for '{subject}' to {recipient_list}: {e}")
        print(f"SMTP Error: {e}")
        return False
