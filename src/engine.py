import time
from tqdm import tqdm
from googleapiclient.errors import HttpError
from .email_utils import create_message, send_gmail_message

# ANSI Colors
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

class EmailSendingError(Exception):
    """Base class for email sending failures."""
    pass

class FatalRateLimitError(EmailSendingError):
    """Raised when Gmail API rate limits are exhausted."""
    pass

class FatalQuotaError(EmailSendingError):
    """Raised when daily sending quota is reached."""
    pass

class FatalAuthError(EmailSendingError):
    """Raised when authentication fails mid-run."""
    pass

class EmailEngine:
    def __init__(self, service, data_manager, template_manager, config):
        self.service = service
        self.data_manager = data_manager
        self.template_manager = template_manager
        self.config = config

    def run(self, is_dry_run=False):
        """Execute the sending process."""
        contacts = self.data_manager.contacts
        sent_emails = self.data_manager.sent_emails
        total_contacts = len(contacts)
        
        sent_count = 0
        skipped_count = 0
        error_count = 0

        print(f"\nProcessing {total_contacts} records...")
        
        pbar = tqdm(contacts.iterrows(), total=total_contacts, desc="Progress")
        for _, row in pbar:
            cmp_name = str(row.get('company_name', '')).strip()
            cmp_email = str(row.get('company_email', '')).strip()
            
            # Skipping logic with clear reasons
            skip_reason = None
            if not cmp_email or cmp_email.lower() == 'nan':
                skip_reason = "Empty email"
            elif cmp_name.startswith('!'):
                skip_reason = "Excluded name (!)"
            elif cmp_email in sent_emails:
                skip_reason = "Already sent"
                
            if skip_reason:
                tqdm.write(f"{YELLOW}Skipping {cmp_name or '[Empty]'}: {skip_reason}{RESET}")
                skipped_count += 1
                continue

            pbar.set_postfix({"Target": cmp_name})

            subject, body = self.template_manager.render(dict(row))
            
            if is_dry_run:
                sent_count += 1
            else:
                msg = create_message(cmp_email, subject, body, self.config.get('ATTACHMENTS'))
                
                try:
                    if self._send_with_retry(msg, cmp_email, cmp_name):
                        sent_count += 1
                    else:
                        error_count += 1
                except EmailSendingError as e:
                    pbar.close()
                    raise e # Re-raise to main.py
                
                # Intra-email delay
                if sent_count + skipped_count + error_count < total_contacts:
                    time.sleep(self.config['WAIT_SECONDS'])

        pbar.close()
        return sent_count, skipped_count, error_count

    def _send_with_retry(self, msg, email, name):
        """Internal helper to handle retries for a single email."""
        retry_count = 0
        max_retries = 3
        wait_time = 15 
        
        while retry_count <= max_retries:
            try:
                send_gmail_message(self.service, msg)
                self.data_manager.log_send(email, name)
                return True
            except HttpError as e:
                status = e.resp.status
                content = e.content.decode('utf-8') if hasattr(e, 'content') else str(e)

                if status == 429:
                    retry_count += 1
                    if retry_count > max_retries:
                        raise FatalRateLimitError(f"Rate limit hit and max retries ({max_retries}) exhausted: {content}")
                    
                    tqdm.write(f"{YELLOW}Rate limit hit. Attempt {retry_count}/{max_retries}. Waiting {wait_time}s...{RESET}")
                    time.sleep(wait_time)
                    wait_time *= 2 # Exponential backoff
                elif status == 403:
                    # Often "User rate limit exceeded" or daily quota
                    if "quota" in content.lower() or "limit" in content.lower():
                        raise FatalQuotaError(f"Daily quota or hard limit exceeded: {content}")
                    # Other 403s might be retryable or specific permissions
                    tqdm.write(f"{RED}Permission error for {name}: {content}{RESET}")
                    return False
                elif status == 401:
                    raise FatalAuthError(f"Authentication session expired: {content}")
                else:
                    tqdm.write(f"{RED}API Error for {name} (Status {status}): {content}{RESET}")
                    return False
            except Exception as e:
                tqdm.write(f"{RED}Unexpected Error for {name}: {e}{RESET}")
                return False
        return False
