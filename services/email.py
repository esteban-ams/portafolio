"""
Email service using Resend API.

Setup:
1. Create account at https://resend.com
2. Get API key from dashboard
3. Add to .env: RESEND_API_KEY=re_xxxxx
4. Verify your domain or use onboarding@resend.dev for testing
"""

import os
import resend
from typing import Optional
from dataclasses import dataclass


@dataclass
class ContactMessage:
    name: str
    email: str
    message: str


def send_contact_email(msg: ContactMessage) -> tuple[bool, Optional[str]]:
    """
    Send contact form submission via Resend.

    Returns:
        (success: bool, error_message: Optional[str])
    """
    api_key = os.getenv('RESEND_API_KEY')
    recipient = os.getenv('CONTACT_EMAIL', 'tu@email.com')

    if not api_key:
        return False, "RESEND_API_KEY not configured"

    resend.api_key = api_key

    # Use Resend's test address if no verified domain
    from_email = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')

    try:
        resend.Emails.send({
            "from": from_email,
            "to": [recipient],
            "subject": f"Nuevo mensaje de contacto: {msg.name}",
            "html": f"""
            <h2>Nuevo mensaje desde tu portfolio</h2>
            <p><strong>Nombre:</strong> {msg.name}</p>
            <p><strong>Email:</strong> <a href="mailto:{msg.email}">{msg.email}</a></p>
            <hr>
            <p><strong>Mensaje:</strong></p>
            <p style="white-space: pre-wrap;">{msg.message}</p>
            """,
            "reply_to": msg.email  # So you can reply directly to the sender
        })
        return True, None
    except Exception as e:
        return False, str(e)
