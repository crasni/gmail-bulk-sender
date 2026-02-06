import os

# ANSI Colors
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

class UI:
    @staticmethod
    def format_size(size):
        """Format bytes to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    @staticmethod
    def show_header(config, args):
        print("Gmail Bulk Sender")
        print(f"Subject Pattern: {config['EMAIL_SUBJECT_FORMAT'].format(company_name='[Company]')}")
        print(f"Contacts: {args.contacts}")
        print(f"Template: {args.template}")
        
        attachments = config.get('ATTACHMENTS', [])
        if isinstance(attachments, str):
            attachments = [attachments]
        if attachments:
            print(f"Attachments: {', '.join([os.path.basename(a) for a in attachments])}")
        else:
            print(f"Attachments: None")

    @staticmethod
    def show_stats(stats, args, contacts_df, sent_emails, attachments_list):
        print(f"\n{YELLOW}Contacts Summary:{RESET}")
        print(f"- Total Records: {stats['total']}")
        if stats['already_sent'] > 0:
            print(f"- Already Sent:  {stats['already_sent']}")
        
        if args.stats:
            print(f"- Missing Email: {stats['missing_email']}")
            print(f"- Tagged Skip (!): {stats['manually_skipped']}")
            
            if attachments_list:
                print(f"\n{YELLOW}Attachment Audit:{RESET}")
                for att in attachments_list:
                    exists = os.path.exists(att)
                    status = f"{GREEN}OK{RESET}" if exists else f"{RED}MISSING{RESET}"
                    size = UI.format_size(os.path.getsize(att)) if exists else "N/A"
                    print(f"- {os.path.basename(att)}: {status} ({size})")
            
            # Upcoming Batch
            upcoming = []
            for _, row in contacts_df.iterrows():
                email = str(row.get('company_email', '')).strip()
                name = str(row.get('company_name', '')).strip()
                if email and not name.startswith('!') and email not in sent_emails:
                    upcoming.append(f"{name} <{email}>")
                if len(upcoming) >= 5:
                    break
            
            if upcoming:
                print(f"\n{YELLOW}Upcoming Batch (Next 5):{RESET}")
                for i, contact in enumerate(upcoming, 1):
                    print(f"{i}. {contact}")
        else:
            if stats['to_be_skipped'] > 0:
                print(f"- To be Skipped: {stats['to_be_skipped']}")
                
        print(f"- Net to Send:   {stats['net_to_send']}")

    @staticmethod
    def show_preview(preview):
        if preview:
            print(f"\n{YELLOW}--- Preview (First pending email) ---{RESET}")
            print(f"To:      {preview['to']}")
            print(f"Subject: {preview['subject']}")
            snippet = preview['body'].split('\n')[0]
            print(f"Body:    {snippet}...")
            print(f"{YELLOW}-------------------------------------{RESET}")
        else:
            print(f"\n{YELLOW}Notice: No pending emails found in the list.{RESET}")

    @staticmethod
    def confirm_start(args):
        if args.dry_run:
            print(f"{YELLOW}Dry run mode enabled. No emails will be sent.{RESET}")
        
        if not args.yes:
            confirm = input("\nConfirm start? (y/n): ")
            return confirm.lower() == 'y'
        return True

    @staticmethod
    def show_interruption(e, config, data_manager):
        from src.engine import FatalRateLimitError, FatalQuotaError, FatalAuthError
        
        print(f"\n{RED}Mission Interrupted!{RESET}")
        
        if isinstance(e, FatalRateLimitError):
            print(f"{YELLOW}Reason: Rate limit reached.{RESET}")
            print(f"Gmail has paused your sending. Please wait at least 30-60 minutes before trying again.")
        elif isinstance(e, FatalQuotaError):
            print(f"{YELLOW}Reason: Daily quota exceeded.{RESET}")
            print(f"You've likely hit the 2,000 emails/day limit (or less for trial accounts).")
            print(f"Please wait 24 hours for the quota to reset.")
        elif isinstance(e, FatalAuthError):
            print(f"{YELLOW}Reason: Authentication failed mid-run.{RESET}")
            print(f"Your session may have expired. Try deleting {YELLOW}{config['TOKEN_FILE']}{RESET} and rerunning.")
        else:
            print(f"{RED}Unexpected error: {e}{RESET}")
            
        print(f"\n{GREEN}Don't worry!{RESET} Your progress is saved in {YELLOW}{config['LOG_FILE']}{RESET}.")
        print(f"When you rerun the script, it will skip the {len(data_manager.sent_emails)} emails already sent.")

    @staticmethod
    def show_final_summary(sent, skipped, errors, dry_run, log_file):
        print(f"\n{GREEN}Mission complete!{RESET}")
        print(f"Successfully processed: {sent}")
        print(f"Failed: {errors}")
        print(f"Skipped: {skipped}")
        if not dry_run:
            print(f"Log updated at: {log_file}")
