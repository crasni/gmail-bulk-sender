import argparse
import os
from config import CONFIG
from src.auth import get_gmail_service
from src.data_manager import DataManager
from src.template_manager import TemplateManager
from src.engine import EmailEngine

# ANSI Colors
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

class CLIHandler:
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Gmail Bulk Sender")
        parser.add_argument("-d", "--dry-run", action="store_true", help="Enable dry run mode (simulation)")
        parser.add_argument("--reset", action="store_true", help="Clear the sent log before starting")
        parser.add_argument("-c", "--contacts", type=str, default=CONFIG['CONTACTS_FILE'], help="Path to contacts CSV")
        parser.add_argument("-t", "--template", type=str, default=CONFIG['TEMPLATE_FILE'], help="Path to email template")
        parser.add_argument("-s", "--stats", action="store_true", help="Show contact list statistics")
        parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
        return parser.parse_args()

def check_requirements(contacts_file, template_file):
    """Initial sanity check for file existence."""
    required = [contacts_file, template_file, CONFIG['CREDENTIALS_FILE']]
    attachments = CONFIG.get('ATTACHMENTS')
    if isinstance(attachments, str):
        required.append(attachments)
    elif isinstance(attachments, list):
        required.extend([a for a in attachments if a])
        
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"{RED}Error: Missing required files: {', '.join(missing)}{RESET}")
        exit(1)

def main():
    args = CLIHandler.parse_args()
    
    # Initialize Managers
    data_manager = DataManager(args.contacts, CONFIG['LOG_FILE'])
    template_manager = TemplateManager(args.template, CONFIG['EMAIL_SUBJECT_FORMAT'])

    if args.reset:
        data_manager.reset_log()
        print(f"{YELLOW}Sent log cleared.{RESET}")

    check_requirements(args.contacts, args.template)

    # Load Data
    try:
        data_manager.load_contacts()
        data_manager.load_sent_log()
        template_manager.load_template()
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        return

    # Header
    print("Gmail Bulk Sender")
    print(f"Subject Pattern: {CONFIG['EMAIL_SUBJECT_FORMAT'].format(company_name='[Company]')}")
    print(f"Contacts: {args.contacts}")
    print(f"Template: {args.template}")

    # Stats
    if args.stats:
        stats = data_manager.get_stats()
        print(f"\n{YELLOW}Contacts Summary:{RESET}")
        print(f"- Total Records: {stats['total']}")
        print(f"- Already Sent:  {stats['already_sent']}")
        print(f"- To be Skipped: {stats['to_be_skipped']}")
        print(f"- Net to Send:   {stats['net_to_send']}")

    # Preview
    preview = template_manager.get_preview(data_manager.contacts, data_manager.sent_emails)
    if preview:
        print(f"\n{YELLOW}--- Preview (First pending email) ---{RESET}")
        print(f"To:      {preview['to']}")
        print(f"Subject: {preview['subject']}")
        snippet = preview['body'].split('\n')[0]
        print(f"Body:    {snippet}...")
        print(f"{YELLOW}-------------------------------------{RESET}")
    else:
        print(f"\n{YELLOW}Notice: No pending emails found in the list.{RESET}")

    if args.dry_run:
        print(f"{YELLOW}Dry run mode enabled. No emails will be sent.{RESET}")

    # Confirmation
    if not args.yes:
        confirm = input("\nConfirm start? (y/n): ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return

    # Gmail Service
    service = None
    if not args.dry_run:
        service = get_gmail_service()
        if not service:
            return

    # Engine Execution
    engine = EmailEngine(service, data_manager, template_manager, CONFIG)
    sent, skipped, errors = engine.run(is_dry_run=args.dry_run)

    # Final Summary
    print(f"\n{GREEN}Mission complete!{RESET}")
    print(f"Successfully processed: {sent}")
    print(f"Failed: {errors}")
    print(f"Skipped: {skipped}")
    if not args.dry_run:
        print(f"Log updated at: {CONFIG['LOG_FILE']}")

if __name__ == '__main__':
    main()
