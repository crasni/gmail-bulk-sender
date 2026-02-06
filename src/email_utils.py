import os.path
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def render_template(template_text, data):
    """Replace placeholders like <<key>> with values from data."""
    for key, value in data.items():
        template_text = template_text.replace(f'<<{key}>>', str(value))
    return template_text

def create_message(to, subject, body, attachments=None):
    """Create a MIME message for Gmail with support for multiple attachments."""
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    # Convert single string to list
    if isinstance(attachments, str):
        attachments = [attachments]
    
    if attachments:
        for attachment in attachments:
            if attachment and os.path.exists(attachment):
                with open(attachment, 'rb') as f:
                    part = MIMEApplication(f.read(), _subtype='pdf')
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
                    message.attach(part)
            
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_gmail_message(service, message_body):
    """Send the message via Gmail API. Let exceptions bubble up for handled retry."""
    return service.users().messages().send(userId='me', body=message_body).execute()
