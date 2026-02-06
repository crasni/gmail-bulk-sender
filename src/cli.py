import argparse
import os

class CLIHandler:
    @staticmethod
    def parse_args(config):
        parser = argparse.ArgumentParser(description="Gmail Bulk Sender")
        parser.add_argument("-d", "--dry-run", action="store_true", help="Enable dry run mode (simulation)")
        parser.add_argument("--reset", action="store_true", help="Clear the sent log before starting")
        parser.add_argument("-c", "--contacts", type=str, default=config['CONTACTS_FILE'], help="Path to contacts CSV")
        parser.add_argument("-t", "--template", type=str, default=config['TEMPLATE_FILE'], help="Path to email template")
        parser.add_argument("-s", "--stats", action="store_true", help="Show contact list statistics")
        parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation prompt")
        parser.add_argument("--setup", action="store_true", help="Show the Google API setup guide")
        return parser.parse_args()
