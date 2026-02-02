import os

# ANSI Colors
YELLOW = "\033[93m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"

def show_setup_guide():
    """Print a step-by-step guide for setting up Google API."""
    print(f"\n{CYAN}--- Gmail Bulk Sender: Setup Assistant ---{RESET}")
    print("\nTo use this tool, you need a Google Cloud project with Gmail API enabled.")
    
    steps = [
        "Go to the Google Cloud Console: https://console.cloud.google.com/",
        "Create a new project (e.g., 'Bulk Mailer').",
        "Search for 'Gmail API' in the top bar and click 'Enable'.",
        "Click 'Create Credentials' -> 'OAuth client ID'.",
        "If asked, configure the 'OAuth consent screen' as 'External' (just fill the app name and email).",
        "IMPORTANT: In the 'Test users' section, add your own Gmail address (and any friends' emails) so Google allows you to log in.",
        "Select Application Type: 'Desktop App' and click 'Create'.",
        "Download the JSON file and rename it to 'credentials.json'.",
        "Place it inside the 'auth/' folder in this project."
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
        
    print(f"\n{GREEN}Once 'auth/credentials.json' is in place, you are ready to send!{RESET}")
    print(f"{YELLOW}Note: On your first run, a browser will open to ask for your permission.{RESET}\n")
