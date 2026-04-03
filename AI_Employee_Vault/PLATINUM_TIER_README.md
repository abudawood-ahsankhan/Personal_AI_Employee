# 🏅 Personal AI Employee - Platinum Tier

**Tagline:** *Always-On Cloud + Local Executive - Production-ready AI Employee*

This is the **Platinum Tier** implementation - the most advanced tier with 24/7 cloud operation, cloud/local separation, vault sync, health monitoring, and A2A messaging.

## 📋 Platinum Tier Deliverables Checklist

From the hackathon document:

- [x] **All Gold requirements** (complete)
- [x] **Cloud VM 24/7 operation** with health monitoring
- [x] **Work-Zone Specialization** (cloud vs local ownership)
- [x] **Delegation via Synced Vault** with claim-by-move rule
- [x] **Security rules** (secrets never sync)
- [x] **Odoo on Cloud VM** integration (draft-only)
- [x] **A2A (Agent-to-Agent) messaging** system
- [x] **Platinum demo workflow** complete
- [x] **Documentation** of architecture

## 🏗️ Platinum Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                     Personal AI Employee                              │
│                        Platinum Tier                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  CLOUD VM (24/7)                       LOCAL MACHINE                 │
│  ┌────────────────────────┐            ┌────────────────────────┐   │
│  │   Cloud Agent          │            │   Local Executive      │   │
│  │                        │            │                        │   │
│  │ OWNS:                  │            │ OWNS:                  │   │
│  │ • Email triage         │◄──────────►│ • Approvals            │   │
│  │ • Draft replies        │  A2A Msg   │ • WhatsApp session     │   │
│  │ • Social drafts        │            │ • Payments/banking     │   │
│  │ • Draft accounting     │            │ • Final send/post      │   │
│  │                        │            │                        │   │
│  │ DRAFT ONLY             │            │ EXECUTION ONLY         │   │
│  └──────────┬─────────────┘            └──────────┬─────────────┘   │
│             │                                      │                 │
│             └────────────┐  ┌─────────────────────┘                 │
│                          │  │                                        │
│             ┌────────────▼──▼────────────────┐                      │
│             │    Vault Sync Manager          │                      │
│             │                                │                      │
│             │  • Bidirectional sync          │                      │
│             │  • Claim-by-move rule          │                      │
│             │  • Security filters            │                      │
│             │  • Signal system               │                      │
│             └────────────┬───────────────────┘                      │
│                          │                                          │
│             ┌────────────▼───────────────────┐                      │
│             │    Health Monitor              │                      │
│             │                                │                      │
│             │  • Heartbeat monitoring        │                      │
│             │  • Auto-restart                │                      │
│             │  • Health reports              │                      │
│             └────────────────────────────────┘                      │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │           Obsidian Vault (Synced)                            │    │
│  │  /Needs_Action/<cloud|local>  /Plans/<cloud|local>          │    │
│  │  /In_Progress/<cloud_agent|local_exec>                       │    │
│  │  /Updates  /Signals  /Messages  /Sync_Exclude               │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **All Gold Tier** components installed
2. **Cloud VM** (Oracle Cloud Free Tier recommended)
3. **SSH access** to cloud VM
4. **Git** installed (for vault sync)

### Step 1: Setup Local Components

```bash
# Already installed with Platinum Tier
cd AI_Employee_Vault
python src\test_platinum_tier.py
```

### Step 2: Deploy to Cloud VM

```bash
# Edit deployment script
notepad deploy_cloud.sh

# Set your VM details
export VM_HOST="your-vm-ip"
export VM_USER="ubuntu"
export VM_KEY="~/.ssh/id_rsa"

# Deploy
bash deploy_cloud.sh
```

### Step 3: Setup Vault Sync

```bash
# Initialize git in vault
cd AI_Employee_Vault
git init

# Add files (secrets excluded)
git add .
git commit -m "Initial Platinum setup"

# Add remote
git remote add cloud ubuntu@your-vm-ip:/opt/ai-employee/vault

# Push to cloud
git push cloud main
```

### Step 4: Test A2A Messaging

```bash
# Test cloud messenger
python src\a2a_messaging.py cloud

# Test local messenger
python src\a2a_messaging.py local
```

## 📁 Platinum Folder Structure

```
AI_Employee_Vault/
├── Needs_Action/
│   ├── cloud/              # Cloud agent tasks
│   └── local/              # Local executive tasks
├── Plans/
│   ├── cloud/              # Cloud-generated plans
│   └── local/              # Local executive plans
├── Pending_Approval/
│   ├── cloud/              # Cloud awaiting approval
│   └── local/              # Local approval queue
├── In_Progress/
│   ├── cloud_agent/        # Cloud agent working
│   └── local_exec/         # Local executive working
├── Updates/                # Synced updates
├── Signals/                # Inter-agent signals
├── Messages/               # A2A messages
│   ├── cloud/
│   │   ├── inbox/
│   │   ├── outbox/
│   │   ├── sent/
│   │   └── received/
│   └── local/
│       ├── inbox/
│       ├── outbox/
│       ├── sent/
│       └── received/
└── Sync_Exclude/           # Never sync these files
```

## 🔧 Platinum Components

### 1. Vault Sync Manager

Manages secure synchronization between Cloud and Local vaults.

**Features:**
- Bidirectional sync with security filters
- Claim-by-move rule (prevents double-work)
- Signal system for notifications
- Never syncs secrets (.env, tokens, credentials)

**Usage:**
```python
from vault_sync import CloudVaultSyncManager, LocalVaultSyncManager

# Cloud side
cloud_sync = CloudVaultSyncManager(vault_path)
cloud_sync.sync_to_cloud(files)
cloud_sync.write_signal('draft_ready', {...})

# Local side
local_sync = LocalVaultSyncManager(vault_path)
local_sync.sync_from_cloud(files)
local_sync.approve_draft(draft_file)
```

### 2. Cloud Agent

Runs 24/7 on cloud VM.

**Responsibilities:**
- Email triage and draft replies (no sending)
- Social post drafts (no posting)
- Draft accounting (no posting)
- Health monitoring

**Usage:**
```bash
# On cloud VM
python src/cloud_agent.py
```

### 3. Local Executive

Runs on local machine.

**Responsibilities:**
- Approve/reject cloud drafts
- Execute WhatsApp actions
- Execute payments/banking
- Final send/post actions
- Merge cloud updates into Dashboard

**Usage:**
```bash
python src/local_executive.py
```

### 4. Health Monitor

Monitors all components and auto-restarts failures.

**Features:**
- Heartbeat monitoring (5 min timeout)
- Auto-restart (max 3 per hour)
- Health reports
- Alert generation

**Usage:**
```bash
python src/health_monitor.py
```

### 5. A2A Messaging

Direct messaging between Cloud Agent and Local Executive.

**Features:**
- Message persistence
- Delivery tracking
- Callback handlers
- Vault audit trail

**Usage:**
```python
from a2a_messaging import CloudA2AMessenger, LocalA2AMessenger

# Cloud sends message
cloud = CloudA2AMessenger(vault_path)
cloud.request_approval('email_send', {'to': 'client@example.com'})

# Local approves
local = LocalA2AMessenger(vault_path)
local.approve_draft('draft_123')
```

## 🔄 Work-Zone Specialization

| Domain | Cloud Owns | Local Owns |
|--------|------------|------------|
| **Email** | Triage, draft replies | Approve, send |
| **Social** | Draft posts, schedule | Approve, post |
| **Accounting** | Draft entries | Approve, post |
| **WhatsApp** | ❌ No access | ✅ Full control |
| **Payments** | ❌ No access | ✅ Full control |

## 🔒 Security Rules

### Never Sync (Sync_Exclude)

These files are NEVER synced between cloud and local:

- `.env` files
- Token files
- Credential files
- Session data (WhatsApp)
- OAuth credentials
- Banking credentials

### Claim-by-Move Rule

1. First agent to move item from `/Needs_Action` to `/In_Progress/<agent>/` owns it
2. Other agents must ignore claimed items
3. Claims expire after 1 hour

## 🎯 Platinum Demo Workflow

### Scenario: Email Arrives While Local is Offline

```
1. Gmail Watcher (Cloud) detects new email
   → Creates EMAIL_*.md in /Needs_Action/cloud

2. Cloud Agent processes email
   → Creates DRAFT_REPLY_*.md in /Updates

3. Cloud Agent writes signal
   → Signals/EMAIL_DRAFT_READY_*.json

4. [Local is offline - no problem!]

5. Cloud Agent waits...

6. Local comes back online
   → Local Executive reads signals
   → Creates approval request in /Pending_Approval/local

7. Human reviews and approves
   → Moves file to /Approved

8. Local Executive executes
   → Sends email via Email MCP
   → Notifies Cloud via A2A
   → Moves to /Done

9. Cloud syncs update
   → Dashboard updated
   → Audit trail complete
```

## 📊 Cloud VM Setup

### Oracle Cloud Free Tier

1. **Sign up:** https://www.oracle.com/cloud/free/
2. **Create VM:** Ubuntu 22.04 (Always Free)
3. **Configure SSH:** Add your public key
4. **Open ports:** 22 (SSH), 443 (HTTPS)

### Deployment

```bash
# Run deployment script
bash deploy_cloud.sh

# Check status
ssh ubuntu@your-vm-ip "sudo systemctl status ai-employee-cloud"

# View logs
ssh ubuntu@your-vm-ip "sudo journalctl -u ai-employee-cloud -f"
```

## 📈 Monitoring

### Health Dashboard

```bash
# Check cloud health
python src/health_monitor.py --once

# View health reports
ls -la AI_Employee_Vault/.health/

# Check A2A messages
ls -la AI_Employee_Vault/Messages/
```

### Alerts

Alerts are created in:
- `Errors/` folder for critical issues
- `Signals/` folder for notifications

## 🐛 Troubleshooting

### Cloud Agent Not Starting

```bash
# SSH to VM
ssh ubuntu@your-vm-ip

# Check service
sudo systemctl status ai-employee-cloud

# View logs
sudo journalctl -u ai-employee-cloud -f

# Restart
sudo systemctl restart ai-employee-cloud
```

### Sync Conflicts

```bash
# Check sync status
python src/vault_sync.py AI_Employee_Vault local

# Force resync
git fetch cloud
git merge cloud/main
```

### A2A Messages Not Delivering

```bash
# Check message folders
ls AI_Employee_Vault/Messages/cloud/inbox/
ls AI_Employee_Vault/Messages/local/inbox/

# Test messaging
python src/a2a_messaging.py cloud
```

## 📚 Resources

- **Gold Tier README:** GOLD_TIER_README.md
- **Hackathon Main Doc:** ../Personal AI Employee Hackathon 0...md
- **Oracle Cloud Free:** https://www.oracle.com/cloud/free/
- **Git Documentation:** https://git-scm.com/doc

## 🏆 Platinum Tier Complete!

You now have a **production-ready AI Employee** with:

- ☁️ **Cloud 24/7:** Always-on email/social processing
- 🖥️ **Local Executive:** Secure approvals and execution
- 🔄 **Vault Sync:** Secure bidirectional sync
- 🏥 **Health Monitor:** Auto-restart on failures
- 💬 **A2A Messaging:** Direct agent communication
- 🔒 **Security:** Secrets never synced
- 📊 **Audit Trail:** Complete logging

---

*Personal AI Employee Platinum Tier v0.1 - Built for Hackathon 0*
*Version: 0.1 (Platinum Tier)*
*Date: March 31, 2026*
