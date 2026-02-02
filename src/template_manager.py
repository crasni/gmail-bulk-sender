import os

class TemplateManager:
    def __init__(self, template_file, subject_format):
        self.template_file = template_file
        self.subject_format = subject_format
        self.template_content = None

    def load_template(self):
        """Read the template file."""
        if not os.path.exists(self.template_file):
            raise FileNotFoundError(f"Template file not found: {self.template_file}")
        with open(self.template_file, 'r', encoding='utf-8') as f:
            self.template_content = f.read()
        return self.template_content

    def render(self, context):
        """Render the template with the provided context dictionary."""
        if self.template_content is None:
            self.load_template()
            
        body = self.template_content
        for key, value in context.items():
            placeholder = f"<<{key}>>"
            body = body.replace(placeholder, str(value))
        
        subject = self.subject_format.format(**context)
        return subject, body

    def get_preview(self, contacts, sent_emails):
        """Generate a preview for the first pending email."""
        for _, row in contacts.iterrows():
            email = str(row.get('company_email', '')).strip()
            name = str(row.get('company_name', '')).strip()
            
            if email and not name.startswith('!') and email not in sent_emails:
                subject, body = self.render(dict(row))
                return {
                    'to': email,
                    'subject': subject,
                    'body': body
                }
        return None
