# 🤖 Personal AI Employee - Bronze Tier

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

This is a **Bronze Tier** implementation of the Personal AI Employee from the [Hackathon 0](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md). It provides the foundational layer for an autonomous AI agent that manages your personal and business affairs using **Claude Code** and **Obsidian**.

## ✨ What This Does

The Bronze Tier provides:

1. **Obsidian Vault Structure** - Organized folders for task management
2. **Dashboard.md** - Real-time summary of your AI employee's activities
3. **Company Handbook** - Rules and guidelines for AI behavior
4. **Business Goals** - Track objectives and metrics
5. **File System Watcher** - Monitors a drop folder and creates action files for Claude to process

## 📁 Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Main status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Objectives and metrics
├── Inbox/                    # Files awaiting processing
├── Needs_Action/             # Action items for Claude
├── Plans/                    # Multi-step task plans
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved actions
├── Rejected/                 # Rejected actions
├── Done/                     # Completed tasks
├── Logs/                     # Activity logs
├── Briefings/                # CEO briefings (future)
├── Accounting/               # Financial records (future)
├── Invoices/                 # Invoice files (future)
└── src/                      # Python watcher scripts
    ├── base_watcher.py       # Base watcher class
    ├── filesystem_watcher.py # File drop watcher
    └── requirements.txt      # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

Ensure you have the following installed:

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base |
| [Claude Code](https://claude.com/claude-code) | Latest | AI reasoning engine |
| [Git](https://git-scm.com) | Latest | Version control |

### Installation

1. **Clone or navigate to the project:**
   ```bash
   cd "E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault"
   ```

2. **Install Python dependencies:**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

3. **Create a Drop folder** (for file watcher):
   ```bash
   mkdir "E:\Hackathon 0\Personal_AI_Employee\Drop"
   ```

4. **Open the vault in Obsidian:**
   - Launch Obsidian
   - Click "Open folder as vault"
   - Select `AI_Employee_Vault` folder

### Running the File System Watcher

1. **Start the watcher:**
   ```bash
   cd "E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault\src"
   python filesystem_watcher.py ..\ "..\..\Drop"
   ```

   Or with custom paths:
   ```bash
   python filesystem_watcher.py /path/to/vault /path/to/drop_folder
   ```

2. **Drop a file** into the Drop folder

3. **Watch it create** an action file in `Needs_Action/` and copy the file to `Inbox/`

4. **Process with Claude Code:**
   ```bash
   claude
   ```
   Then prompt: *"Check the Needs_Action folder and process any pending items"*

## 🔄 How It Works

### The Watcher Pattern

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Drop Folder │────▶│ File Watcher │────▶│ Needs_Action/   │
│ (New Files) │     │ (Python)     │     │ (Action Files)  │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │   Claude Code   │
                                          │   (Reasoning)   │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │   Dashboard.md  │
                                          │   (Update)      │
                                          └─────────────────┘
```

### File Drop Flow

1. **You drop a file** (e.g., `invoice.pdf`) into the Drop folder
2. **Watcher detects** the new file within 30 seconds
3. **Copies file** to `Inbox/invoice.pdf`
4. **Creates action file** in `Needs_Action/FILE_<hash>_<timestamp>.md` with:
   - File metadata (size, type, hash)
   - Suggested actions based on file type
   - Checklist for processing
5. **Claude Code reads** the action file and processes it
6. **Moves to Done** when complete

## 📋 Bronze Tier Deliverables Checklist

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System)
- [x] Claude Code successfully reading/writing to vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [ ] All AI functionality implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

For Bronze Tier, only these are needed:
```
VAULT_PATH=/path/to/your/AI_Employee_Vault
DROP_FOLDER=/path/to/your/Drop
DEV_MODE=true
DRY_RUN=true
```

### Watcher Settings

Edit `filesystem_watcher.py` to customize:
- `check_interval`: How often to check for new files (default: 30s)
- File categorization rules
- Suggested actions per file type

## 🧪 Testing

### Test the File Watcher

1. **Start the watcher** (keep terminal open):
   ```bash
   cd src
   python filesystem_watcher.py ..\ "..\..\Drop"
   ```

2. **Create a test file:**
   ```bash
   echo "Test content" > "../Drop/test_document.txt"
   ```

3. **Verify:**
   - File copied to `Inbox/test_document.txt`
   - Action file created in `Needs_Action/FILE_*`

4. **Process with Claude:**
   ```bash
   claude --prompt "Check Needs_Action folder and process pending items"
   ```

## 📊 Next Steps (Silver Tier)

To upgrade to Silver Tier, add:

1. **Gmail Watcher** - Monitor email for urgent messages
2. **WhatsApp Watcher** - Detect keywords in messages
3. **MCP Server** - Send emails automatically
4. **Approval Workflow** - Human-in-the-loop for sensitive actions
5. **Scheduled Tasks** - Daily briefings via cron/Task Scheduler

## 🛡️ Security Notes

- **Never commit `.env`** - Contains credentials
- **Never commit tokens** - Store in environment variables only
- **Review before approving** - Always check action files before moving to Approved
- **Start in DEV_MODE** - Test thoroughly before enabling real actions

## 📚 Documentation

- [Dashboard.md](./Dashboard.md) - Main status overview
- [Company_Handbook.md](./Company_Handbook.md) - AI behavior rules
- [Business_Goals.md](./Business_Goals.md) - Objectives tracking
- [Hackathon Guide](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md) - Full documentation

## 🤝 Support

- **Weekly Research Meeting:** Wednesdays 10:00 PM PKT
- **Zoom:** [Join here](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **YouTube:** [Panaversity](https://www.youtube.com/@panaversity)

## 📄 License

This project is part of Hackathon 0 - Personal AI Employee.

---

*Built with ❤️ for the Personal AI Employee Hackathon 0*  
*Version: 0.1.0 (Bronze Tier)*
