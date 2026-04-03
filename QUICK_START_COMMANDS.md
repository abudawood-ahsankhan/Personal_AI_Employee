# 🚀 Personal AI Employee - Quick Start Commands

## ⚡ Quick Start (After OAuth Setup)

### Step 1: Authenticate Qwen Code (First Time Only)
```bash
qwen auth
# Select: Qwen OAuth
# Complete login in browser
```

### Step 2: Test Qwen Code
```bash
qwen -p "Hello! I'm ready to use Personal AI Employee."
```

### Step 3: Run the System
```bash
cd E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault
python src\orchestrator.py
```

---

## 📋 Complete Command Reference

### 🔐 Authentication Commands

```bash
# Authenticate (first time)
qwen auth

# Check authentication status
dir C:\Users\LEnovo\.qwen\oauth_creds.json

# Test Qwen Code
qwen -p "Hello!"
```

---

### 🏃 Run Full System

```bash
# Start orchestrator (continuous mode)
cd E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault
python src\orchestrator.py

# Run once and exit (test mode)
python src\orchestrator.py --once

# With custom vault path
python src\orchestrator.py --vault "E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault"
```

---

### 🧪 Test Commands

```bash
# Run full test suite
cd E:\Hackathon 0\Personal_AI_Employee
test_suite.bat

# Test individual components
python AI_Employee_Vault\src\plan_generator.py
python AI_Employee_Vault\src\ceo_briefing.py
python AI_Employee_Vault\src\ralph_wiggum.py
python AI_Employee_Vault\src\audit_logger.py

# Run Gold Tier verification
python AI_Employee_Vault\src\test_gold_tier.py AI_Employee_Vault
```

---

### 📂 File Operations

```bash
# View Needs_Action folder
dir AI_Employee_Vault\Needs_Action

# View Plans folder
dir AI_Employee_Vault\Plans

# View Done folder
dir AI_Employee_Vault\Done

# View Briefings
dir AI_Employee_Vault\Briefings

# View Logs
dir AI_Employee_Vault\Logs\Audit
```

---

### 🤖 Qwen Code Commands

```bash
# Simple prompt
qwen -p "Process all files in Needs_Action folder"

# With specific model
qwen --model qwen3.5-plus -p "Create a plan for processing emails"

# Interactive mode
qwen
> Process all pending tasks
> Create CEO briefing for this week
> /help

# Process specific file
qwen -p "Read AI_Employee_Vault/Needs_Action/TEST_ACTION_001.md and create a plan"

# Generate social media post
qwen -p "Create LinkedIn post from Dashboard.md updates"

# Generate invoice
qwen -p "Create invoice for Client A based on completed tasks"
```

---

### 🔧 Component Commands

#### Plan Generator
```bash
cd AI_Employee_Vault
python src\plan_generator.py
```

#### CEO Briefing Generator
```bash
python src\ceo_briefing.py
```

#### Ralph Wiggum Loop
```bash
python src\ralph_wiggum.py
```

#### Audit Logger
```bash
python src\audit_logger.py
```

#### Error Recovery Check
```bash
python src\error_recovery.py
```

---

### 🌐 MCP Server Commands

#### Install MCP Dependencies
```bash
cd AI_Employee_Vault\src

cd mcp-odoo && npm install
cd ..\mcp-facebook && npm install
cd ..\mcp-twitter && npm install
cd ..\mcp-email && npm install
cd ..\mcp-linkedin && npm install
```

#### Test MCP Servers
```bash
# Odoo (requires Odoo installation)
cd src\mcp-odoo
node index.js

# Facebook (requires API credentials)
cd src\mcp-facebook
node index.js

# Twitter (requires API credentials)
cd src\mcp-twitter
node index.js

# Email (requires SMTP config)
cd src\mcp-email
node index.js

# LinkedIn (requires API credentials)
cd src\mcp-linkedin
node index.js
```

---

### 📊 Monitoring Commands

```bash
# Check Ollama status (if using local models)
ollama list
ollama ps

# Check Qwen Code version
qwen --version

# View system processes
tasklist | findstr python
tasklist | findstr node
tasklist | findstr ollama
```

---

### 🛠️ Configuration Commands

```bash
# Edit environment file
notepad AI_Employee_Vault\.env

# Edit Qwen settings
notepad C:\Users\LEnovo\.qwen\settings.json

# View Qwen credentials
dir C:\Users\LEnovo\.qwen
```

---

## 📅 Daily Workflow

### Morning (8:00 AM)
```bash
# Generate daily briefing
qwen -p "Generate daily briefing from yesterday's activities"

# Check pending actions
dir AI_Employee_Vault\Needs_Action
```

### During Day
```bash
# Process new emails/files
python src\orchestrator.py --once

# Check status
python src\test_gold_tier.py AI_Employee_Vault
```

### Evening (6:00 PM)
```bash
# Review completed tasks
dir AI_Employee_Vault\Done

# Check audit logs
python src\audit_logger.py
```

---

## 🎯 Common Scenarios

### Scenario 1: Process New Email
```bash
# 1. Gmail watcher creates file in Needs_Action
# 2. Run orchestrator
python src\orchestrator.py --once

# 3. Or use Qwen directly
qwen -p "Process new email in Needs_Action folder"
```

### Scenario 2: Generate Weekly Report
```bash
# Generate CEO briefing
python src\ceo_briefing.py

# Or use Qwen
qwen -p "Generate weekly CEO briefing from this week's data"
```

### Scenario 3: Post to LinkedIn
```bash
# Using LinkedIn poster
python src\linkedin_poster.py --post "Your message here"

# Or use Qwen + MCP
qwen -p "Post to LinkedIn: Business update from Dashboard.md"
```

### Scenario 4: Create Invoice
```bash
# Using Qwen + Odoo MCP
qwen -p "Create invoice for Client A, $500, for consulting services"
```

---

## 🐛 Troubleshooting Commands

### Qwen Code Issues
```bash
# Check installation
qwen --version

# Re-authenticate
qwen auth

# Clear credentials and re-authenticate
del C:\Users\LEnovo\.qwen\oauth_creds.json
qwen auth
```

### Python Issues
```bash
# Check Python installation
C:\Users\LEnovo\AppData\Local\Python\bin\python.exe --version

# Reinstall dependencies
pip install -r AI_Employee_Vault\src\requirements.txt
```

### Node.js Issues
```bash
# Check Node.js installation
node --version
npm --version

# Reinstall MCP dependencies
cd AI_Employee_Vault\src
npm install
```

---

## 📞 Quick Reference Card

| Task | Command |
|------|---------|
| **Authenticate** | `qwen auth` |
| **Test Qwen** | `qwen -p "Hello"` |
| **Run System** | `python orchestrator.py` |
| **Test All** | `test_suite.bat` |
| **Generate Plans** | `python plan_generator.py` |
| **CEO Briefing** | `python ceo_briefing.py` |
| **View Logs** | `python audit_logger.py` |
| **Check Status** | `test_gold_tier.py` |

---

## 🎉 You're Ready!

Pick a command and start using your Personal AI Employee Gold Tier!

```bash
# Start here:
qwen -p "Hello! Help me process my pending tasks."
```

---

*Personal AI Employee - Gold Tier Command Reference*
*Updated: March 31, 2026*
