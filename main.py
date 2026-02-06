import os
from config import CONFIG
from src.auth import get_gmail_service
from src.data_manager import DataManager
from src.template_manager import TemplateManager
from src.engine import EmailEngine
from src.setup_assistant import show_setup_guide
from src.cli import CLIHandler
from src.ui import UI, YELLOW, GREEN, RED, RESET

def check_credentials():
    """Verify credentials.json exists."""
    if not os.path.exists(CONFIG['CREDENTIALS_FILE']):
        print(f"{RED}Error: {CONFIG['CREDENTIALS_FILE']} not found.{RESET}")
        print(f"Run {YELLOW}python main.py --setup{RESET} for a guide on how to get it.")
        exit(1)

def main():
    args = CLIHandler.parse_args(CONFIG)
    
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

    # Display Information
    UI.show_header(CONFIG, args)
    
    stats = data_manager.get_stats()
    attachments = CONFIG.get('ATTACHMENTS', [])
    if isinstance(attachments, str):
        attachments = [attachments]
    
    UI.show_stats(stats, args, data_manager.contacts, data_manager.sent_emails, attachments)

    if stats['net_to_send'] == 0:
        print(f"\n{RED}Warning: No emails to send.{RESET}")
        if stats['already_sent'] == stats['total']:
            print(f"Tip: All contacts in {args.contacts} are already in the sent log.")
            print(f"Use {YELLOW}--reset{RESET} if you want to resend to everyone.")
        return

    # Preview
    preview = template_manager.get_preview(data_manager.contacts, data_manager.sent_emails)
    UI.show_preview(preview)

    # Confirmation
    if not UI.confirm_start(args):
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
    try:
        sent, skipped, errors = engine.run(is_dry_run=args.dry_run)
        UI.show_final_summary(sent, skipped, errors, args.dry_run, CONFIG['LOG_FILE'])
            
    except Exception as e:
        UI.show_interruption(e, CONFIG, data_manager)
        # We don't re-raise here because UI.show_interruption handled the user-facing part
        # and main() is the entry point.

if __name__ == '__main__':
    main()
