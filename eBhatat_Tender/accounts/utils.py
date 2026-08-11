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
    Auto-injects 'sent_at' (formatted IST timestamp) into context so all templates can display
    the exact email send time.
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

        # 2. Pre-flight: warn if SMTP password is missing (common on fresh deployments)
        smtp_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        if not smtp_password:
            logger.warning(
                "send_ebharat_email: EMAIL_HOST_PASSWORD is not set. "
                "Email will likely fail. Set this environment variable in your deployment "
                "(e.g. Render Dashboard → Environment Variables)."
            )

        # 3. Get safe from_email
        from_email = (
            getattr(settings, 'DEFAULT_FROM_EMAIL', None)
            or getattr(settings, 'EMAIL_HOST_USER', None)
            or 'ebharattender@gmail.com'
        )

        # 4. Auto-inject sent_at timestamp so all templates can display the send time
        from django.utils import timezone
        try:
            from zoneinfo import ZoneInfo
            ist = ZoneInfo('Asia/Kolkata')
            now_ist = timezone.now().astimezone(ist)
            sent_at_str = now_ist.strftime('%d %b %Y, %I:%M %p IST')
        except Exception:
            from datetime import datetime
            sent_at_str = datetime.now().strftime('%d %b %Y, %I:%M %p')

        merged_context = dict(context or {})
        merged_context.setdefault('sent_at', sent_at_str)

        # 5. Render HTML content safely
        try:
            template_path = f'emails/{template_name}' if not template_name.startswith('emails/') else template_name
            html_content = render_to_string(template_path, merged_context)
        except Exception as te:
            logger.error(f"Template rendering error for {template_name}: {te}")
            html_content = f"<h2>{subject}</h2><p>Please check your account portal for details.</p>"

        # 6. Strip tags for plain text
        text_content = strip_tags(html_content)

        # 7. Build email object
        email = EmailMultiAlternatives(
            subject=f"{subject} | eBharat Tender",
            body=text_content,
            from_email=from_email,
            to=clean_recipients
        )

        email.attach_alternative(html_content, "text/html")

        # 8. Attach any files safely
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

        # 9. Send email safely with fail_silently=False wrapped in exception handler
        sent_count = email.send(fail_silently=False)
        return bool(sent_count)

    except Exception as e:
        logger.error(f"SMTP / Email dispatch error for '{subject}' to {recipient_list}: {e}")
        print(f"SMTP Error: {e}")
        return False


def send_email_in_background(subject, template_name, context, recipient_list, attachments=None):
    """
    Triggers send_ebharat_email asynchronously in a background daemon thread.
    This guarantees that email sending will NEVER block the main Django HTTP request/response cycle,
    preventing Gunicorn worker timeouts even if SMTP hangs or fails on Render.
    """
    import threading
    thread = threading.Thread(
        target=send_ebharat_email,
        args=(subject, template_name, context, recipient_list, attachments),
        daemon=True
    )
    thread.start()
    return True

