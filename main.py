import argparse
import os
from config import CONFIG
from src.auth import get_gmail_service
from src.data_manager import DataManager
from src.template_manager import TemplateManager
from src.engine import EmailEngine
from src.setup_assistant import show_setup_guide

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
        parser.add_argument("--setup", action="store_true", help="Show the Google API setup guide")
        return parser.parse_args()

def check_credentials():
    """Verify credentials.json exists."""
    if not os.path.exists(CONFIG['CREDENTIALS_FILE']):
        print(f"{RED}Error: {CONFIG['CREDENTIALS_FILE']} not found.{RESET}")
        print(f"Run {YELLOW}python main.py --setup{RESET} for a guide on how to get it.")
        exit(1)

def main():
    args = CLIHandler.parse_args()
    
    if args.setup:
        show_setup_guide()
        return

    # Initialize Managers
    data_manager = DataManager(args.contacts, CONFIG['LOG_FILE'])
    template_manager = TemplateManager(args.template, CONFIG['EMAIL_SUBJECT_FORMAT'])

    if args.reset:
        data_manager.reset_log()
        print(f"{YELLOW}Sent log cleared.{RESET}")

    # Check/Generate Contacts
    if not os.path.exists(args.contacts):
        print(f"{YELLOW}Notice: {args.contacts} not found.{RESET}")
        gen = input("Would you like to generate a sample contacts file? (y/n): ")
        if gen.lower() == 'y':
            data_manager.generate_template()
            print(f"{GREEN}Created {args.contacts}. Please fill it and rerun.{RESET}")
        return

    # Check/Generate Template
    if not os.path.exists(args.template):
        print(f"{YELLOW}Notice: {args.template} not found.{RESET}")
        gen = input("Would you like to generate a sample template file? (y/n): ")
        if gen.lower() == 'y':
            template_manager.generate_template()
            print(f"{GREEN}Created {args.template}. Please edit it and rerun.{RESET}")
        return

    check_credentials()

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

    # Stats (Always shown for clarity)
    stats = data_manager.get_stats()
    print(f"\n{YELLOW}Contacts Summary:{RESET}")
    print(f"- Total Records: {stats['total']}")
    if stats['already_sent'] > 0:
        print(f"- Already Sent:  {stats['already_sent']}")
    if stats['to_be_skipped'] > 0:
        print(f"- To be Skipped: {stats['to_be_skipped']}")
    print(f"- Net to Send:   {stats['net_to_send']}")

    if stats['net_to_send'] == 0:
        print(f"\n{RED}Warning: No emails to send.{RESET}")
        if stats['already_sent'] == stats['total']:
            print(f"Tip: All contacts in {args.contacts} are already in the sent log.")
            print(f"Use {YELLOW}--reset{RESET} if you want to resend to everyone.")
        return

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
