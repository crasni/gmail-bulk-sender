# Gmail Bulk Sender Configuration

CONFIG = {
    'SCOPES': ['https://www.googleapis.com/auth/gmail.send'],
    
    # Files
    'CONTACTS_FILE': 'data/contacts.csv',    # CSV with company_name, company_email
    'TEMPLATE_FILE': 'assets/template.txt', # Email body template (<<company_name>>)
    'ATTACHMENTS': [
        'assets/2026系卡企劃書.pdf', 
        # 'assets/another_file.pdf'
    ], # Can be a single string or a list of strings
    'CREDENTIALS_FILE': 'auth/credentials.json',
    'TOKEN_FILE': 'auth/token.json',
    'LOG_FILE': 'data/sent_log.csv',     # Track sent emails to avoid duplicates
    
    # Email Settings
    'EMAIL_SUBJECT_FORMAT': "【合作邀請】臺大資訊系卡 × {company_name} 宣傳與贊助合作提案",
    'WAIT_SECONDS': 3,                  # Anti-spam delay
}
