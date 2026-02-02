# Gmail Bulk Sender

A tool for sending bulk emails via the Gmail API with automatic resume, rate-limit protection, and safety previews.

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/crasni/gmail-bulk-sender.git
   cd gmail-bulk-sender
   ```

2. **Install Python & Virtual Environment** (Python 3.10+ recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # or .venv\Scripts\activate on Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Google API Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - Enable the **Gmail API**.
   - Create **OAuth 2.0 Desktop Credentials**.
   - In the "OAuth consent screen" settings, add the sender's email to the **"Test users"** list.
   - Save the JSON as `auth/credentials.json`.
   - On the first run, a browser will open for authentication. The script will save a `token.json` in `auth/` automatically.
   - **Note**: Google may show a "Google hasn't verified this app" warning. Click **Advanced** -> **Go to [Project Name] (unsafe)** to continue.

4. **Prepare Files**:
   - **Contacts**: Fill `data/contacts.csv`. It **must** have `company_name` and `company_email` columns.
   - **Template**: Edit `assets/template.txt`. Use `<<column_name>>` for variables (e.g., `Hello <<company_name>>`).
   - **Settings**: Adjust the subject and wait times in `config.py`.

## Usage

### Simple Run
```bash
python main.py
```
Before sending, the tool will:
1.  Verify all files exist.
2.  Show a **Preview** of the first rendered email.
3.  Ask for final confirmation.

### CLI Flags
| Flag | Shortcut | Description |
| :--- | :--- | :--- |
| `--dry-run` | `-d` | Simulate the process without sending emails. |
| `--reset` | | Delete history and start fresh. |
| `--stats` | `-s` | Show a breakdown of the contact list (Sent vs Pending). |
| `--yes` | `-y` | Skip the confirmation prompt (dangerous). |
| `--setup` | | Show the Google API setup guide. |
| `--contacts`| `-c` | Specify a custom contacts file path. |
| `--template`| `-t` | Specify a custom template file path. |

### Practical Examples
- **Check list health**: `python main.py --stats`
- **Simulate fresh run**: `python main.py --reset --dry-run`
- **Use a specific list**: `python main.py -c data/custom_list.csv`

## Technical Notes
- **Resumability**: The script tracks sent emails in `data/sent_log.csv`. If it stops, just run it again; it will skip those already logged.
- **Manual Skip**: If you add a `!` at the start of a `company_name` in the CSV, the script will skip that row.
- **Rate Limits**: Includes automatic 10s-40s wait intervals if Google API rate limits (429/403) are triggered.
