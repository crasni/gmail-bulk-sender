# Gmail Bulk Sender Roadmap 🚀

This roadmap outlines the evolution of this script from a technical prototype to a user-friendly tool for everyone.

## Phase 1: Robust Foundation (Current Focus)
*Goal: Prevent common errors and make setup easy.*

- [ ] **Dependency Management**: Create `requirements.txt` for easy installation.
- [ ] **Config Separation**: Move hardcoded constants (filenames, subjects) to a clear configuration section.
- [ ] **Friendly Error Messages**: Detect missing files and provide actionable instructions instead of crashing.
- [ ] **Dry Run Mode**: Allow users to see who will be emailed without actually sending.

## Phase 2: User Experience (UX)
*Goal: Make it comfortable for non-technical users.*

- [ ] **Progress Tracking**: Add a visual progress bar (using `tqdm`) to show status.
- [ ] **Sent Log**: Automatically create a `sent_emails.csv` to track what has been sent.
- [ ] **Resumability**: If the script stops, it should automatically skip emails already logged in `sent_emails.csv`.
- [ ] **Template Preview**: Print the first rendered email for final confirmation.

## Phase 3: Additional Features (Current)
*Goal: Add core capabilities.*

- [x] **Multi-Attachment Support**: Send multiple PDFs or documents in one go.
- [x] **Rate Limiting Intelligence**: Automatically detect Google API limits, wait, and retry with backoff.
- [x] **CLI Flags**: Switched from interactive prompts to command-line flags.
- [x] **Log Reset**: Added a `--reset` flag to clear the sent history.
- [ ] **Progress Tracking**: Add a visual progress bar (using `tqdm`) to show status.

## Phase 4: Distribution
*Goal: Zero installation setup.*

- [ ] **Executable (.exe/.app)**: Package the script using PyInstaller so friends don't even need to install Python.
- [ ] **Setup Wizard**: A script to help users set up their Google Cloud Console credentials.
