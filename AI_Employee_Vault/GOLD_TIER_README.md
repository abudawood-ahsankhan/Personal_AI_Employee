# 🏆 Personal AI Employee - Gold Tier

**Tagline:** *Fully autonomous digital employee with cross-domain integration and comprehensive audit*

This is the **Gold Tier** implementation of the Personal AI Employee Hackathon. It includes full cross-domain integration, multiple MCP servers, Odoo ERP integration, social media automation, error recovery, and the Ralph Wiggum persistence loop.

## 📋 Gold Tier Deliverables Checklist

From the hackathon requirements:

- [x] **All Silver requirements** (watchers, planning, approval workflow, scheduling)
- [x] **Full cross-domain integration** (Personal + Business)
- [x] **Odoo Community ERP integration** via MCP server
- [x] **Facebook and Instagram integration** for posting and summaries
- [x] **Twitter (X) integration** for posting and summaries
- [x] **Multiple MCP servers** for different action types (5 total)
- [x] **Weekly Business and Accounting Audit** with CEO Briefing generation
- [x] **Error recovery and graceful degradation** system
- [x] **Comprehensive audit logging** with immutable hash chaining
- [x] **Ralph Wiggum loop** for autonomous multi-step task completion
- [x] **Documentation** of architecture and components

## 🏗️ Gold Tier Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Personal AI Employee - Gold Tier                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                  │
│  │   Gmail      │  │  WhatsApp    │  │  File Drop   │                  │
│  │   Watcher    │  │   Watcher    │  │   Watcher    │                  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                  │
│         │                 │                  │                           │
│         └─────────────────┼──────────────────┘                           │
│                           │                                              │
│                           ▼                                              │
│                  ┌─────────────────┐                                     │
│                  │   Orchestrator  │                                     │
│                  │   + Ralph       │                                     │
│                  │   Wiggum Loop   │                                     │
│                  └────────┬────────┘                                     │
│                           │                                              │
│         ┌─────────────────┼─────────────────┐                           │
│         │                 │                 │                            │
│         ▼                 ▼                 ▼                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │   Error     │  │   Audit     │  │    CEO      │                      │
│  │  Recovery   │  │   Logger    │  │  Briefing   │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
│                           │                                              │
│         ┌─────────────────┼─────────────────┐                           │
│         │                 │                 │                            │
│         ▼                 ▼                 ▼                            │
│  ┌─────────────────────────────────────────────────────┐                │
│  │              MCP Server Layer                        │                │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │                │
│  │  │Odoo  │ │Facebook│ │Twitter│ │Email │ │LinkedIn│ │                │
│  │  │ ERP  │ │/Instagram│ │ (X)  │ │ SMTP │ │       │ │                │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘     │                │
│  └─────────────────────────────────────────────────────┘                │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────┐           │
│  │           Obsidian Vault (Memory & State)                │           │
│  │  /Inbox  /Needs_Action  /Plans  /In_Progress  /Done     │           │
│  │  /Pending_Approval  /Approved  /Rejected  /Errors       │           │
│  │  /Briefings  /Logs/Audit  /Accounting  /Social          │           │
│  │  /Quarantine  /Failed  /Tasks  /Updates                 │           │
│  └──────────────────────────────────────────────────────────┘           │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.13+** installed
2. **Node.js 24+** (for MCP servers)
3. **Claude Code** subscription
4. **Obsidian** (for vault GUI)
5. **Odoo Community** (optional - for ERP features)

### Step 1: Install Dependencies

```bash
cd AI_Employee_Vault/src

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install MCP server dependencies
cd mcp-odoo && npm install
cd ../mcp-facebook && npm install
cd ../mcp-twitter && npm install
cd ../mcp-email && npm install
cd ../mcp-linkedin && npm install
```

### Step 2: Configure Environment

```bash
# In AI_Employee_Vault folder
copy .env.example .env
```

Edit `.env` with your credentials for each service you want to use.

### Step 3: Configure MCP Servers

Add to your Claude Code settings (`%APPDATA%\Claude\claude_config.json` on Windows):

```json
{
  "mcpServers": {
    "odoo": {
      "command": "node",
      "args": ["E:/Hackathon 0/Personal_AI_Employee/AI_Employee_Vault/src/mcp-odoo/index.js"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DATABASE": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "admin"
      }
    },
    "facebook": {
      "command": "node",
      "args": ["E:/Hackathon 0/Personal_AI_Employee/AI_Employee_Vault/src/mcp-facebook/index.js"],
      "env": {
        "FACEBOOK_ACCESS_TOKEN": "your_token",
        "FACEBOOK_PAGE_ID": "your_page_id",
        "INSTAGRAM_ACCOUNT_ID": "your_ig_id"
      }
    },
    "twitter": {
      "command": "node",
      "args": ["E:/Hackathon 0/Personal_AI_Employee/AI_Employee_Vault/src/mcp-twitter/index.js"],
      "env": {
        "TWITTER_API_KEY": "your_key",
        "TWITTER_API_SECRET": "your_secret",
        "TWITTER_ACCESS_TOKEN": "your_token",
        "TWITTER_ACCESS_SECRET": "your_secret"
      }
    },
    "email": {
      "command": "node",
      "args": ["E:/Hackathon 0/Personal_AI_Employee/AI_Employee_Vault/src/mcp-email/index.js"],
      "env": {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "your_email@gmail.com",
        "SMTP_PASSWORD": "your_app_password"
      }
    },
    "linkedin": {
      "command": "node",
      "args": ["E:/Hackathon 0/Personal_AI_Employee/AI_Employee_Vault/src/mcp-linkedin/index.js"],
      "env": {
        "LINKEDIN_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### Step 4: Run the System

```bash
# Run the full Gold Tier system
python orchestrator.py

# Or run individual components
python ralph_wiggum.py      # Autonomous task completion
python ceo_briefing.py      # Generate weekly briefing
python audit_logger.py      # View audit logs
```

## 📁 Gold Tier Folder Structure

```
AI_Employee_Vault/
├── src/                        # Source code
│   ├── base_watcher.py         # Base watcher class
│   ├── gmail_watcher.py        # Gmail monitor
│   ├── whatsapp_watcher.py     # WhatsApp monitor
│   ├── linkedin_poster.py      # LinkedIn auto-poster
│   ├── plan_generator.py       # Creates Plan.md files
│   ├── approval_manager.py     # Approval workflow
│   ├── orchestrator.py         # Main controller
│   │
│   ├── ralph_wiggum.py         # Ralph Wiggum persistence loop ⭐ NEW
│   ├── error_recovery.py       # Error recovery system ⭐ NEW
│   ├── audit_logger.py         # Comprehensive audit logging ⭐ NEW
│   ├── ceo_briefing.py         # Weekly CEO briefing generator ⭐ NEW
│   │
│   ├── mcp-odoo/               # Odoo ERP integration ⭐ NEW
│   │   ├── index.js
│   │   ├── package.json
│   │   └── .env.example
│   ├── mcp-facebook/           # Facebook/Instagram MCP ⭐ NEW
│   │   ├── index.js
│   │   ├── package.json
│   │   └── .env.example
│   ├── mcp-twitter/            # Twitter (X) MCP ⭐ NEW
│   │   ├── index.js
│   │   ├── package.json
│   │   └── .env.example
│   ├── mcp-email/              # Email (SMTP) MCP ⭐ NEW
│   │   ├── index.js
│   │   ├── package.json
│   │   └── .env.example
│   └── mcp-linkedin/           # LinkedIn MCP (from Silver)
│       ├── index.js
│       ├── package.json
│       └── .env.example
│
├── Inbox/                      # Raw incoming items
├── Needs_Action/               # Items requiring action
├── Plans/                      # Generated action plans
├── In_Progress/                # Currently being processed ⭐ NEW
├── Tasks/                      # Ralph Wiggum task queue ⭐ NEW
├── Pending_Approval/           # Awaiting human approval
├── Approved/                   # Approved, ready to execute
├── Rejected/                   # Rejected items
├── Done/                       # Completed items
├── Failed/                     # Failed tasks ⭐ NEW
├── Errors/                     # Error alerts ⭐ NEW
├── Quarantine/                 # Quarantined items ⭐ NEW
├── Briefings/                  # Daily/Weekly briefings
├── Logs/
│   └── Audit/                  # Immutable audit logs ⭐ NEW
├── Accounting/                 # Financial records
├── Invoices/                   # Invoice files
├── Social/                     # Social media posts ⭐ NEW
└── Updates/                    # Cross-agent updates ⭐ NEW
```

## 🔧 Gold Tier Components

### 1. Ralph Wiggum Persistence Loop ⭐ NEW

Autonomous task completion system that keeps Claude working until tasks are done.

**Features:**
- Automatic retry on incomplete tasks
- Completion criteria checking
- Task state management
- Iteration limiting

**Usage:**
```python
from ralph_wiggum import RalphWiggumLoop

ralph = RalphWiggumLoop(vault_path='/path/to/vault')

# Create a task
task = ralph.create_task(
    prompt="Process all emails and send responses",
    task_type='email',
    priority='high'
)

# Run the task (loops until complete)
ralph.run_task(task)
```

### 2. Error Recovery System ⭐ NEW

Handles errors with graceful degradation and automatic recovery.

**Features:**
- Error categorization (transient, auth, logic, data, system)
- Exponential backoff retry
- Circuit breaker pattern
- Quarantine for review
- Human alerting

**Usage:**
```python
from error_recovery import ErrorRecoveryManager

error_mgr = ErrorRecoveryManager(vault_path)

@error_mgr.with_retry(ErrorRecoveryManager.TRANSIENT)
def call_external_api():
    # Will retry automatically on transient errors
    ...
```

### 3. Comprehensive Audit Logging ⭐ NEW

Immutable audit trail with hash chaining for compliance.

**Features:**
- SHA-256 hash chaining (immutable)
- Daily log rotation
- Searchable entries
- Export capabilities
- 90-day retention

**Usage:**
```python
from audit_logger import get_audit_logger

audit = get_audit_logger(vault_path)

# Log actions
audit.log_action(
    actor='claude_code',
    action='send_email',
    target='client@example.com',
    result='success'
)

audit.log_decision(
    actor='claude_code',
    decision='request_approval',
    context='payment_500',
    reasoning='Amount exceeds threshold'
)

# Search logs
results = audit.search(actor='claude_code', date_from='2026-03-01')
```

### 4. CEO Briefing Generator ⭐ NEW

Automated weekly business and accounting audits.

**Features:**
- Revenue summary
- Task completion stats
- Goals progress tracking
- Bottleneck identification
- Proactive suggestions

**Usage:**
```python
from ceo_briefing import CEOBriefingGenerator

generator = CEOBriefingGenerator(vault_path)

# Generate weekly briefing
briefing = generator.generate_weekly_briefing()

# Briefing saved to /Briefings/Weekly_CEO_Briefing_YYYY-MM-DD.md
```

### 5. Odoo ERP MCP Server ⭐ NEW

Integrates with Odoo Community Edition for accounting and business management.

**Tools:**
- `create_invoice` - Create customer invoices
- `get_invoices` - Retrieve invoices
- `get_partners` - Get customers/vendors
- `create_partner` - Add new partner
- `get_products` - Get product catalog
- `register_payment` - Record payments
- `get_accounting_summary` - Financial summary

### 6. Facebook/Instagram MCP Server ⭐ NEW

Posts to Facebook Pages and Instagram Business accounts.

**Tools:**
- `post_to_facebook` - Create Facebook post
- `post_to_instagram` - Create Instagram post
- `get_facebook_insights` - Page analytics
- `get_instagram_insights` - Instagram analytics
- `get_recent_posts` - Recent posts
- `generate_social_summary` - Combined summary

### 7. Twitter (X) MCP Server ⭐ NEW

Posts to Twitter and retrieves analytics.

**Tools:**
- `post_tweet` - Create tweet
- `post_thread` - Create tweet thread
- `get_timeline` - User tweets
- `get_tweet_metrics` - Tweet analytics
- `get_account_metrics` - Account stats
- `search_tweets` - Search Twitter

### 8. Email MCP Server ⭐ NEW

Sends emails via SMTP (Gmail, Outlook, custom).

**Tools:**
- `send_email` - Send email
- `send_invoice_email` - Send invoice with PDF
- `send_bulk_email` - Bulk sending with rate limiting
- `verify_email_config` - Test SMTP config

## 📊 Gold Tier vs Silver Tier

| Feature | Silver Tier | Gold Tier |
|---------|-------------|-----------|
| **Watchers** | 2 (Gmail, WhatsApp) | 3+ (Gmail, WhatsApp, File) |
| **MCP Servers** | 1 (LinkedIn) | 5 (Odoo, FB, Twitter, Email, LinkedIn) |
| **Social Media** | LinkedIn only | LinkedIn + Facebook + Instagram + Twitter |
| **Error Handling** | Basic | Advanced with circuit breakers |
| **Audit Logging** | Basic | Immutable with hash chaining |
| **Task Persistence** | Single-run | Ralph Wiggum loop |
| **Business Intelligence** | Manual | Automated CEO briefings |
| **ERP Integration** | None | Odoo Community |

## 🔒 Security & Compliance

### Audit Trail
- All actions logged with SHA-256 hash chaining
- 90-day retention (configurable)
- Exportable for compliance reviews

### Error Handling
- Credentials never logged
- Sensitive data quarantined
- Human alerts for critical errors

### Approval Workflow
- Sensitive actions require approval
- All approvals logged
- Rejection tracking

## 📈 Monitoring & Observability

### Audit Logs
```bash
# View today's audit logs
python audit_logger.py search --date today

# Export weekly audit
python audit_logger.py export --output weekly_audit.json --from 2026-03-01 --to 2026-03-07
```

### Error Status
```bash
# View error recovery status
python error_recovery.py status
```

### Daily Summary
```bash
# Get daily audit summary
python audit_logger.py summary --date 2026-03-29
```

## 🎯 Example Workflows

### 1. Invoice → Payment Flow (Full Gold Tier)

```
1. Gmail Watcher detects invoice request
   → Creates EMAIL_*.md in /Needs_Action

2. Plan Generator creates invoice plan
   → Creates PLAN_*.md in /Plans

3. Ralph Wiggum Loop processes plan
   → Claude creates invoice in Odoo via MCP
   → Logs action in Audit

4. Approval Manager detects payment needed
   → Creates APPROVAL_*.md in /Pending_Approval

5. Human approves (moves to /Approved)

6. Approval Manager executes payment
   → Registers payment in Odoo
   → Sends confirmation email via Email MCP
   → Posts business update to LinkedIn

7. Task moved to /Done
   → All actions logged in Audit
```

### 2. Social Media Cross-Posting

```
1. Claude creates business update
   → Writes to /Social/update.md

2. Social MCP servers post to:
   - LinkedIn (via mcp-linkedin)
   - Facebook (via mcp-facebook)
   - Twitter (via mcp-twitter)
   - Instagram (via mcp-facebook)

3. Analytics collected next day
   → Insights stored in /Social/analytics.md
   → Included in weekly CEO briefing
```

### 3. Weekly CEO Briefing

```
Every Monday at 8:00 AM:

1. CEO Briefing Generator runs
   → Collects revenue data from Accounting/
   → Analyzes task completion from Done/
   → Reviews goals from Business_Goals.md
   → Identifies bottlenecks
   → Generates suggestions

2. Briefing saved to /Briefings/
   → Revenue summary
   → Task statistics
   → Goals progress
   → Bottlenecks
   → Recommendations

3. Human CEO reviews briefing
   → Makes strategic decisions
   → Updates Business_Goals.md
```

## 🐛 Troubleshooting

### Ralph Wiggum Loop Not Completing

**Issue:** Task keeps looping without completing

**Solution:**
- Check completion criteria in task
- Review Claude output in `In_Progress/*_output.md`
- Increase `max_iterations` if task is complex

### MCP Server Not Connecting

**Issue:** MCP server fails to connect

**Solution:**
- Check Node.js version (24+)
- Verify npm install completed
- Check environment variables in .env
- Test server manually: `node index.js`

### Audit Logs Not Writing

**Issue:** Audit entries not appearing

**Solution:**
- Check Logs/Audit folder permissions
- Call `audit.flush()` to force write
- Check disk space

### Odoo Connection Failed

**Issue:** Cannot connect to Odoo

**Solution:**
- Verify Odoo is running: `http://localhost:8069`
- Check database name in .env
- Verify username/password
- Check Odoo logs

## 📚 Resources

- [Hackathon Main Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Silver Tier README](SILVER_TIER_README.md)
- [Odoo JSON-RPC API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Meta Graph API](https://developers.facebook.com/docs/graph-api)
- [Twitter API v2](https://developer.twitter.com/en/docs/twitter-api)
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)

## 🏆 Gold Tier Complete!

You now have a **fully autonomous AI employee** with:

- 👁️ **Senses:** Gmail, WhatsApp, File watchers
- 🧠 **Brain:** Claude Code with Ralph Wiggum persistence
- ✋ **Hands:** 5 MCP servers (Odoo, Social, Email)
- 📊 **Intelligence:** CEO briefing generator
- 🛡️ **Safety:** Error recovery, audit logging
- 📋 **Compliance:** Immutable audit trail

---

*Personal AI Employee Gold Tier v0.1 - Built for Hackathon 0*
*Version: 0.1 (Gold Tier)*
*Date: March 29, 2026*
