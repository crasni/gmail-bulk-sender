# Gmail Bulk Sender

A clean, modular tool for sending bulk emails via the Gmail API with automatic resume, rate-limit protection, and safety previews.

---

## Setup

### 1. Installation
```bash
# Clone the project
git clone https://github.com/crasni/gmail-bulk-sender.git
cd gmail-bulk-sender

# Setup environment (Python 3.10+ recommended)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Google API Configuration
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Enable the **Gmail API**.
3.  Create **OAuth 2.0 Desktop Credentials**.
4.  **Important**: In "OAuth consent screen", add the sender's email to **"Test users"**.
5.  Save the JSON as `auth/credentials.json`.

> [NOTE]
> Google may show an "App not verified" warning on first login. Click **Advanced** -> **Go to [Project] (unsafe)** to proceed safely.

### 3. Data Preparation
- **Contacts**: Fill `data/contacts.csv` (Headers: `company_name`, `company_email`).
- **Template**: Edit `assets/template.txt` (Use `<<placeholder>>` variables).
- **Config**: Set subject and intervals in `config.py`.

---

## Usage

### Commands
```bash
python main.py [flags]
```

### CLI Flags
| Flag | Shortcut | Description |
| :--- | :--- | :--- |
| `--dry-run` | `-d` | Run without sending real emails. |
| `--stats` | `-s` | Show a breakdown of the contact list. |
| `--reset` | | Delete sent history and start fresh. |
| `--setup` | | Show the interactive setup guide. |
| `--yes` | `-y` | Skip final confirmation (automation). |
| `--contacts` | `-c` | Specify a custom contacts file path. |
| `--template` | `-t` | Specify a custom template file path. |

---

## Key Features

- **Automatic Resume**: Progress is tracked in `data/sent_log.csv`. If interrupted, the script skips already-sent entries.
- **Rate-Limit Handling**: Automatically manages Google API 403/429 errors with exponential backoff.
- **Manual Skip**: Add a `!` at the start of any `company_name` in the CSV to skip that row.

### Practical Examples
- **Check list health**: `python main.py --stats`
- **Simulate fresh run**: `python main.py --reset --dry-run`
- **Use a specific list**: `python main.py -c data/custom_list.csv`

---

*Created by [crasni](https://github.com/crasni)*
