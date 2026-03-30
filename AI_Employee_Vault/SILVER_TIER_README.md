# Personal AI Employee - Silver Tier

**Tagline:** *Your autonomous digital assistant with proactive monitoring and human-in-the-loop approvals*

This is the **Silver Tier** implementation of the Personal AI Employee Hackathon. It includes multiple watchers, automated planning, approval workflows, and social media integration.

## 📋 Silver Tier Deliverables Checklist

- [x] All Bronze requirements (Vault, Dashboard, basic watchers)
- [x] **Two or more Watcher scripts** (Gmail + WhatsApp)
- [x] **LinkedIn auto-posting** capability
- [x] **Claude reasoning loop** with Plan.md generation
- [x] **MCP server** for external actions (LinkedIn)
- [x] **Human-in-the-loop approval workflow**
- [x] **Basic scheduling** via orchestrator

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Personal AI Employee                          │
│                        (Silver Tier)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Gmail      │  │  WhatsApp    │  │  LinkedIn    │          │
│  │   Watcher    │  │   Watcher    │  │   Poster     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                  │                   │
│         └─────────────────┼──────────────────┘                   │
│                           │                                      │
│                           ▼                                      │
│                  ┌─────────────────┐                             │
│                  │  Orchestrator   │                             │
│                  │  (Controller)   │                             │
│                  └────────┬────────┘                             │
│                           │                                      │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                    │
│         ▼                 ▼                 ▼                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │    Plan     │  │  Approval   │  │   Claude    │              │
│  │  Generator  │  │  Workflow   │  │    Code     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                  │
│  ┌──────────────────────────────────────────────────┐           │
│  │           Obsidian Vault (Memory)                │           │
│  │  /Inbox  /Needs_Action  /Plans  /Approved       │           │
│  │  /Done   /Pending_Approval  /Briefings  /Logs   │           │
│  └──────────────────────────────────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.13+** installed
2. **Node.js 24+** (for MCP servers)
3. **Claude Code** subscription
4. **Obsidian** (for vault GUI)

### Step 1: Install Dependencies

```bash
# Navigate to src folder
cd AI_Employee_Vault/src

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install LinkedIn MCP dependencies
cd mcp-linkedin
npm install
```

### Step 2: Configure Environment

Copy the example environment file and fill in your credentials:

```bash
# In AI_Employee_Vault folder
copy .env.example .env
```

Edit `.env` with your actual values:

```env
# Vault paths
VAULT_PATH=E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault

# Gmail (optional - for Gmail Watcher)
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret

# LinkedIn (optional - for auto-posting)
LINKEDIN_ACCESS_TOKEN=your_token

# General settings
DEV_MODE=true
DRY_RUN=true
LOG_LEVEL=INFO
```

### Step 3: Setup Gmail Watcher (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to `AI_Employee_Vault/src/`
6. Run once to authenticate:
   ```bash
   python gmail_watcher.py
   ```

### Step 4: Setup LinkedIn Poster

```bash
# Login to LinkedIn (saves session)
cd AI_Employee_Vault/src
python linkedin_poster.py --login
```

Scan the QR code / login in the browser. Session will be saved.

### Step 5: Run the System

#### Option A: Run Individual Components

```bash
# Terminal 1: Gmail Watcher
python gmail_watcher.py

# Terminal 2: WhatsApp Watcher
python whatsapp_watcher.py

# Terminal 3: Approval Manager
python approval_manager.py

# Terminal 4: Orchestrator
python orchestrator.py
```

#### Option B: Run Orchestrator (Recommended)

```bash
# Run orchestrator (manages everything)
python orchestrator.py

# Or run once (process and exit)
python orchestrator.py --once
```

## 📁 Folder Structure

```
AI_Employee_Vault/
├── .env                      # Your environment variables (DO NOT COMMIT)
├── .env.example              # Template for .env
├── Dashboard.md              # Main dashboard
├── Business_Goals.md         # Your business objectives
├── Company_Handbook.md       # Rules and guidelines
├── Inbox/                    # Raw incoming items
├── Needs_Action/             # Items requiring action
├── Plans/                    # Generated action plans
├── Pending_Approval/         # Awaiting human approval
├── Approved/                 # Approved, ready to execute
├── Rejected/                 # Rejected items
├── Done/                     # Completed items
├── Briefings/                # Daily/Weekly briefings
├── Logs/                     # Action logs
├── Accounting/               # Financial records
├── Invoices/                 # Invoice files
└── src/                      # Source code
    ├── base_watcher.py       # Base watcher class
    ├── gmail_watcher.py      # Gmail monitor
    ├── whatsapp_watcher.py   # WhatsApp monitor
    ├── linkedin_poster.py    # LinkedIn auto-poster
    ├── plan_generator.py     # Creates Plan.md files
    ├── approval_manager.py   # Approval workflow
    ├── orchestrator.py       # Main controller
    └── mcp-linkedin/         # LinkedIn MCP server
        ├── index.js
        ├── package.json
        └── .env.example
```

## 🔧 Components

### 1. Gmail Watcher

Monitors Gmail for new unread messages and creates action files.

**Features:**
- OAuth 2.0 authentication
- Priority detection (urgent, invoice, payment keywords)
- Session caching (no re-authentication needed)
- Creates structured Markdown files in `/Needs_Action`

**Usage:**
```bash
python gmail_watcher.py
```

### 2. WhatsApp Watcher

Monitors WhatsApp Web for messages with priority keywords.

**Features:**
- Browser-based (no API needed)
- Session persistence
- Keyword filtering (urgent, invoice, payment, etc.)
- Creates action files with message content

**Usage:**
```bash
# First run (visible browser for QR scan)
python whatsapp_watcher.py

# Subsequent runs (headless)
# Set headless=False in code for first run
```

### 3. LinkedIn Poster

Posts to LinkedIn automatically or with approval.

**Features:**
- Browser automation (no API required)
- Session persistence
- Business update generation from Dashboard
- Human approval option

**Usage:**
```bash
# Login once
python linkedin_poster.py --login

# Post message
python linkedin_poster.py --post "Hello LinkedIn!"

# Post business update
python linkedin_poster.py --business
```

### 4. Plan Generator

Analyzes action files and creates structured Plan.md files.

**Features:**
- Type-specific templates (email, whatsapp, payment, etc.)
- Step-by-step task breakdown
- Checkbox tracking
- Claude Code ready

**Usage:**
```bash
python plan_generator.py
```

### 5. Approval Manager

Human-in-the-loop approval workflow.

**Features:**
- Watches `/Pending_Approval` for requests
- Notifies human of pending items
- Executes approved actions
- Handles rejections gracefully

**Workflow:**
1. AI creates approval request → `/Pending_Approval`
2. Human reviews file
3. Human moves to `/Approved` or `/Rejected`
4. Approved actions execute automatically

**Usage:**
```bash
python approval_manager.py
```

### 6. Orchestrator

Main controller that coordinates all components.

**Features:**
- Runs all watchers
- Triggers Claude Code processing
- Scheduled tasks (daily briefings, weekly audits)
- Central logging

**Usage:**
```bash
# Continuous mode
python orchestrator.py

# Run once
python orchestrator.py --once

# With custom vault
python orchestrator.py --vault /path/to/vault
```

## 🤖 Claude Code Integration

### Configure Claude Code

Add to your Claude Code settings (`~/.config/claude-code/mcp.json`):

```json
{
  "mcpServers": {
    "linkedin": {
      "command": "node",
      "args": ["/path/to/mcp-linkedin/index.js"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### Example Claude Prompts

```bash
# Process all pending actions
claude -p "Check /Needs_Action folder, create plans for new items, and process them"

# Generate daily briefing
claude -p "Review this week's activities and generate a CEO briefing in /Briefings"

# Handle approval requests
claude -p "Check /Pending_Approval and summarize items waiting for approval"
```

## 📅 Scheduled Tasks

Default schedule (configurable in `orchestrator.py`):

| Task | Schedule | Description |
|------|----------|-------------|
| Daily Briefing | 8:00 AM | Summary of pending/completed items |
| Weekly Audit | Monday 9:00 AM | Comprehensive business review |
| Process Actions | Every 5 min | Check and process new actions |

## 🔒 Security

### Credential Management

- Never commit `.env` file (it's in `.gitignore`)
- Use environment variables for all secrets
- Rotate credentials monthly

### Human-in-the-Loop

Sensitive actions require approval:
- Payments over $50
- New payees
- Bulk email sends
- Social media posts (optional)

### Dry Run Mode

Enable dry run for testing:

```env
DRY_RUN=true
```

This logs intended actions without executing them.

## 📊 Monitoring

### Check Status

```bash
# View dashboard
cat Dashboard.md

# View pending actions
ls Needs_Action/

# View active plans
ls Plans/

# View pending approvals
ls Pending_Approval/

# View logs
cat Logs/*.md
```

### Live Monitoring

Use the download monitor script:

```bash
# From project root
powershell -ExecutionPolicy Bypass -File download_monitor.ps1
```

## 🐛 Troubleshooting

### Gmail Watcher Issues

**Error: Credentials not found**
- Ensure `credentials.json` is in `AI_Employee_Vault/src/`
- Check file permissions

**Error: Token expired**
- Delete `token.json` and re-run to re-authenticate

### WhatsApp Watcher Issues

**QR code not scanning**
- Run with `headless=False` for first run
- Ensure stable internet connection

**Session not saving**
- Check `whatsapp_session` folder permissions

### LinkedIn Poster Issues

**Not logged in**
- Run `python linkedin_poster.py --login`
- Wait for full page load before closing

**Post fails**
- Check LinkedIn session
- Verify post length (< 3000 chars)

### General Issues

**Orchestrator not starting**
- Check Python version (3.13+)
- Install dependencies: `pip install -r requirements.txt`

**Claude Code not responding**
- Verify subscription is active
- Check network connection

## 📝 Example Workflow

### Email → Response Flow

1. **Gmail Watcher** detects new email → Creates `EMAIL_*.md` in `/Needs_Action`
2. **Orchestrator** triggers **Plan Generator** → Creates `PLAN_*.md` in `/Plans`
3. **Claude Code** reads plan → Drafts response
4. If response needed → Creates `/Pending_Approval/EMAIL_Reply_*.md`
5. **Human** reviews → Moves to `/Approved`
6. **Approval Manager** executes → Sends email → Moves to `/Done`

### WhatsApp → Invoice Flow

1. **WhatsApp Watcher** detects "invoice" keyword → Creates action file
2. **Plan Generator** creates invoice plan
3. **Claude Code** generates invoice details
4. **Human** approves via `/Approved` folder
5. **LinkedIn Poster** posts business update (optional)

## 🎯 Next Steps (Gold Tier)

To upgrade to Gold Tier, add:
- [ ] Odoo ERP integration
- [ ] Facebook/Instagram posting
- [ ] Twitter (X) integration
- [ ] Multiple MCP servers
- [ ] Weekly CEO Briefing automation
- [ ] Error recovery systems
- [ ] Ralph Wiggum persistence loop

## 📚 Resources

- [Hackathon Main Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Claude Code Docs](https://claude.com/claude-code)
- [Obsidian Help](https://help.obsidian.md/)
- [Playwright Docs](https://playwright.dev/python/)
- [MCP Introduction](https://modelcontextprotocol.io/introduction)

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `/Logs` folder
3. Check hackathon documentation
4. Join Wednesday Research Meeting (Zoom link in main doc)

---

*Personal AI Employee Silver Tier v0.1 - Built for Hackathon 0*
