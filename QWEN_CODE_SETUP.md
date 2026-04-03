# Qwen Code CLI Configuration for Personal AI Employee

## ✅ Installation Complete

**Qwen Code CLI v0.13.2** installed successfully!

## 🔐 Authentication Setup (FREE - 1000 requests/day)

### Option 1: OAuth Authentication (Recommended - FREE)

1. **Start Qwen Code:**
   ```bash
   qwen
   ```

2. **Login:**
   - Type `/auth` command
   - Select **Qwen OAuth**
   - Login with your Qwen Chat account
   - Complete authentication

3. **Benefits:**
   - ✅ **1000 free API calls per day**
   - ✅ No API key needed
   - ✅ Automatic token refresh

### Option 2: API Key (Pay-as-you-go)

1. **Get API Key:**
   - Go to [Alibaba Cloud Bailian Console](https://bailian.console.aliyun.com/)
   - Create API Key

2. **Configure:**
   Edit `C:\Users\LEnovo\.qwen\settings.json`:
   ```json
   {
     "env": {
       "BAILIAN_API_KEY": "your_api_key_here"
     },
     "model": {
       "name": "qwen3.5-plus"
     }
   }
   ```

## 🚀 Using Qwen Code with Personal AI Employee

### Replace Claude Code with Qwen Code

In all scripts and documentation, replace:
- `claude` → `qwen`
- `claude-sonnet-4-5-20250929` → `qwen3.5-plus`

### Example Commands

```bash
# Process emails with Qwen
qwen -p "Check /Needs_Action folder and process all email actions"

# Generate plans with Qwen
qwen -p "Read action files and create Plan.md files for each"

# Run with specific model
qwen --model qwen3.5-plus -p "Your prompt here"

# Interactive mode
qwen
> /help
> Process all pending tasks in Needs_Action folder
```

### Update Orchestrator for Qwen Code

Edit `AI_Employee_Vault/src/orchestrator.py`:

```python
# Change from:
self.claude_model = self.config.get('claude_model', 'claude-sonnet-4-5-20250929')
cmd = ['claude']

# To:
self.qwen_model = self.config.get('qwen_model', 'qwen3.5-plus')
cmd = ['qwen']
cmd.extend(['--model', self.qwen_model])
```

## 📊 Qwen Code vs Claude Code

| Feature | Claude Code | Qwen Code CLI |
|---------|-------------|---------------|
| **Cost** | $20/month | FREE (1000/day) |
| **Model** | Claude Sonnet | Qwen 3.5 Plus |
| **Context** | 200K tokens | 256K tokens |
| **Speed** | Fast | Very Fast |
| **Setup** | Subscription | OAuth (instant) |

## 🔧 Configuration Files

### Global Settings
Location: `C:\Users\LEnovo\.qwen\settings.json`

### Project Settings
Location: `E:\Hackathon 0\Personal_AI_Employee\.qwen\settings.json`

### Credentials
Location: `C:\Users\LEnovo\.qwen\oauth_creds.json` (auto-created after OAuth login)

## 📝 Quick Start Guide

```bash
# 1. Verify installation
qwen --version

# 2. Login (first time)
qwen
> /auth
> Select Qwen OAuth
> Login

# 3. Test it
qwen -p "Hello! What can you help me with?"

# 4. Use with Personal AI Employee
cd E:\Hackathon 0\Personal_AI_Employee\AI_Employee_Vault
qwen -p "Process all files in Needs_Action folder"
```

## 🎯 Integration with Personal AI Employee

### Updated Workflow

```
1. Watcher detects change → Creates action file
2. Orchestrator triggers → qwen (instead of claude)
3. Qwen processes → Creates Plan.md
4. Ralph Wiggum loop → Continues until complete
5. Actions executed → Via MCP servers
6. Results logged → Audit trail
```

### Sample Qwen Prompts

```bash
# Email processing
qwen -p "Read all email action files in Needs_Action and draft responses"

# Invoice generation
qwen -p "Create invoice for Client A based on completed tasks this week"

# Social media post
qwen -p "Generate LinkedIn post about our business updates from Dashboard.md"

# Weekly briefing
qwen -p "Analyze this week's activities and generate CEO briefing"
```

## 🆘 Troubleshooting

### "Command not found: qwen"
- Restart terminal after installation
- Check PATH: `C:\Users\LEnovo\AppData\Roaming\npm`

### "Authentication required"
- Run `qwen` and type `/auth`
- Complete OAuth login

### "Rate limit exceeded"
- Free tier: 1000 requests/day
- Wait until next day or add API key

### "Model not found"
- Use `qwen3.5-plus` or `qwen3-coder`
- Check available models in settings

## 📚 Resources

- **Qwen Code Docs:** https://qwenlm.github.io/qwen-code-docs/
- **Qwen Chat:** https://chat.qwen.ai
- **Alibaba Cloud:** https://bailian.console.aliyun.com/

---

*Personal AI Employee - Qwen Code CLI Configuration*
*Updated: March 29, 2026*
