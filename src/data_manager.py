import os
import pandas as pd
from datetime import datetime

class DataManager:
    def __init__(self, contacts_file, log_file):
        self.contacts_file = contacts_file
        self.log_file = log_file
        self.contacts = None
        self.sent_emails = set()

    def load_contacts(self):
        """Read the contacts CSV file."""
        if not os.path.exists(self.contacts_file):
            raise FileNotFoundError(f"Contacts file not found: {self.contacts_file}")
        self.contacts = pd.read_csv(self.contacts_file)
        return self.contacts

    def load_sent_log(self):
        """Load sent emails from the log file."""
        if not os.path.exists(self.log_file):
            self.sent_emails = set()
            return self.sent_emails
        
        try:
            df = pd.read_csv(self.log_file)
            self.sent_emails = set(df['email'].unique())
        except Exception:
            self.sent_emails = set()
        return self.sent_emails

    def log_send(self, email, name):
        """Record a successful send in the log file."""
        file_exists = os.path.exists(self.log_file)
        log_data = {
            'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            'name': [name],
            'email': [email]
        }
        df = pd.DataFrame(log_data)
        df.to_csv(self.log_file, mode='a', index=False, header=not file_exists)
        self.sent_emails.add(email)

    def reset_log(self):
        """Delete the existing log file."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
            self.sent_emails = set()

    def get_stats(self):
        """Calculate statistics about the contacts list."""
        if self.contacts is None:
            self.load_contacts()
        
        total = len(self.contacts)
        already_sent = 0
        skipped_tag = 0
        to_send = 0
        
        for _, row in self.contacts.iterrows():
            email = str(row.get('company_email', '')).strip()
            name = str(row.get('company_name', '')).strip()
            
            is_empty_email = not email or email.lower() == 'nan'
            is_skip_tag = name.startswith('!')
            
            if is_empty_email or is_skip_tag:
                skipped_tag += 1
            elif email in self.sent_emails:
                already_sent += 1
            else:
                to_send += 1
                
        return {
            'total': total,
            'already_sent': already_sent,
            'to_be_skipped': skipped_tag,
            'net_to_send': to_send
        }

    def generate_template(self):
        """Create a sample contacts.csv file."""
        os.makedirs(os.path.dirname(self.contacts_file), exist_ok=True)
        df = pd.DataFrame({
            'company_name': ['Example Corp', '!Ignore This Line'],
            'company_email': ['hello@example.com', 'test@test.com']
        })
        df.to_csv(self.contacts_file, index=False)
