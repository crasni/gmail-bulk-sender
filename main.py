from __future__ import print_function
import os.path, base64, pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import time

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
# CONTACTS = 'contacts.csv'
# CONTACTS = ''
CONTACTS = 'test.csv'
TEMPLATE = 'template.txt'
PDF = '2026系卡企劃書.pdf'
SUBJECT = "【合作邀請】臺大資訊系卡 × {company_name} 宣傳與贊助合作提案"

def get_service():
    print("正在獲取寄信權限...")
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    print("獲取成功！")
    return build('gmail', 'v1', credentials=creds)

def render_template(template_text, data):
    for key, value in data.items():
        template_text = template_text.replace(f'<<{key}>>', str(value))
    return template_text

def send_email(service, to, subject, body, attachment=None):
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['subject'] = subject
    message.attach(MIMEText(body, 'plain', 'utf-8'))

    if attachment and os.path.exists(attachment):
        with open(attachment, 'rb') as f:
            part = MIMEApplication(f.read(), _subtype='pdf')
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
            message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

def confirm_action(msg):
    ans = input(msg)
    if ans.lower() != 'y':
        print("已取消")
        exit(0)

if __name__ == '__main__':
    missing = [p for p in [CONTACTS, TEMPLATE, PDF, "credentials.json"] if not os.path.exists(p)]
    if missing:
        raise FileNotFoundError(f"以下必要檔案不存在：{', '.join(missing)}")

    confirm_action(f"標題：{SUBJECT.format(company_name='COMPANY_NAME')}\n是否正確？（y/n）")

    service = get_service()
    contacts = pd.read_csv(CONTACTS)
    with open(TEMPLATE, 'r', encoding='utf-8') as f:
        template = f.read()

    sent_company = set()
    for _, row in contacts.iterrows():
        cmp_name = str(row['company_name']).strip()
        if cmp_name.startswith('!') or cmp_name in sent_company:
            print("❌ 跳過重複")
            continue

        body = render_template(template, dict(row))
        subject = SUBJECT.format(company_name=row["company_name"])
        send_email(service, row['company_email'], subject, body, PDF)
        print(f"✅ 已寄給 {row['company_name']} ({row['company_email']})")
        sent_company.add(cmp_name)
        time.sleep(3) # avoid spam
