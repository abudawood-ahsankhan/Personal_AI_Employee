"""
Orchestrator - Main Controller for Personal AI Employee (Silver Tier)
Part of Personal AI Employee Silver Tier

The Orchestrator:
1. Runs all Watcher scripts
2. Triggers Claude Code to process action files
3. Creates plans from actions
4. Manages approval workflow
5. Handles scheduled tasks (daily briefings, etc.)

Usage:
    python orchestrator.py
    python orchestrator.py --once  # Run once and exit
"""

import os
import sys
import time
import logging
import subprocess
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """
    Main orchestrator for the Personal AI Employee system.
    Coordinates all watchers, Claude Code processing, and scheduled tasks.
    """
    
    def __init__(self, vault_path: str, config: Dict = None):
        self.vault_path = Path(vault_path)
        self.config = config or {}
        
        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        
        # Ensure folders exist
        for folder in [self.needs_action, self.plans, self.done, 
                       self.logs, self.pending_approval]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Configuration
        self.check_interval = self.config.get('check_interval', 60)
        self.qwen_model = self.config.get('qwen_model', 'qwen3.5-plus')  # Qwen Code CLI
        self.claude_model = self.config.get('claude_model', 'claude-sonnet-4-5-20250929')  # Fallback
        self.max_iterations = self.config.get('max_iterations', 10)
        
        # Scheduled tasks
        self.scheduled_tasks = []
        
        # Watcher processes
        self.watcher_threads = []
        self.stop_flag = False
    
    def add_scheduled_task(self, task: Dict):
        """Add a scheduled task"""
        self.scheduled_tasks.append(task)
        self.logger.info(f"Added scheduled task: {task.get('name', 'unknown')}")
    
    def check_scheduled_tasks(self):
        """Check and execute due scheduled tasks"""
        now = datetime.now()
        
        for task in self.scheduled_tasks:
            # Check if task is due
            if self._is_task_due(task, now):
                self.logger.info(f"Executing scheduled task: {task.get('name')}")
                self._execute_task(task)
    
    def _is_task_due(self, task: Dict, now: datetime) -> bool:
        """Check if a scheduled task is due"""
        schedule = task.get('schedule', {})
        
        # Simple time-based check
        if 'time' in schedule:
            task_time = datetime.strptime(schedule['time'], '%H:%M').time()
            now_time = now.time()
            
            # Check if within 1 minute of scheduled time
            time_diff = abs((now_time.hour - task_time.hour) * 60 + 
                           (now_time.minute - task_time.minute))
            if time_diff <= 1:
                # Check if already executed today
                last_run = task.get('last_run', '')
                today = now.strftime('%Y-%m-%d')
                if last_run != today:
                    return True
        
        return False
    
    def _execute_task(self, task: Dict):
        """Execute a scheduled task"""
        task_type = task.get('type', 'general')
        
        if task_type == 'daily_briefing':
            self._run_daily_briefing()
        elif task_type == 'weekly_audit':
            self._run_weekly_audit()
        elif task_type == 'process_actions':
            self._process_all_actions()
        
        # Update last run time
        task['last_run'] = datetime.now().strftime('%Y-%m-%d')
    
    def _run_daily_briefing(self):
        """Generate daily briefing"""
        self.logger.info("Running daily briefing generation")
        
        briefing_date = datetime.now().strftime('%Y-%m-%d')
        briefing_file = self.vault_path / 'Briefings' / f'{briefing_date}_Daily_Briefing.md'
        
        # Check if already generated today
        if briefing_file.exists():
            self.logger.info("Daily briefing already exists for today")
            return
        
        # Generate briefing content
        content = self._generate_briefing_content()
        
        briefing_file.write_text(content, encoding='utf-8')
        self.logger.info(f"Daily briefing created: {briefing_file}")
    
    def _generate_briefing_content(self) -> str:
        """Generate daily briefing content from vault data"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Count actions in different folders
        needs_action_count = len(list(self.needs_action.glob('*.md')))
        plans_count = len(list(self.plans.glob('*.md')))
        done_today = len([f for f in self.done.glob('*.md') 
                         if f.stat().st_mtime > (datetime.now() - timedelta(days=1)).timestamp()])
        
        content = f'''---
generated: {datetime.now().isoformat()}
date: {today}
type: daily_briefing
---

# Daily Briefing - {today}

## Summary
- **Pending Actions:** {needs_action_count}
- **Active Plans:** {plans_count}
- **Completed Today:** {done_today}

## Pending Actions
'''
        
        # List pending actions
        for action_file in list(self.needs_action.glob('*.md'))[:10]:
            content += f"- {action_file.stem}\n"
        
        content += f'''
## Active Plans
'''
        
        # List active plans
        for plan_file in list(self.plans.glob('*.md'))[:10]:
            content += f"- {plan_file.stem}\n"
        
        content += f'''
## Recommendations
- Review pending actions in /Needs_Action
- Approve/reject items in /Pending_Approval
- Check completed items in /Done

---
*Generated by AI Employee Orchestrator v0.1*
'''
        
        return content
    
    def _run_weekly_audit(self):
        """Run weekly business audit"""
        self.logger.info("Running weekly audit")
        
        # Similar to daily briefing but more comprehensive
        audit_date = datetime.now().strftime('%Y-%m-%d')
        audit_file = self.vault_path / 'Briefings' / f'{audit_date}_Weekly_Audit.md'
        
        content = f'''---
generated: {datetime.now().isoformat()}
type: weekly_audit
---

# Weekly Business Audit

## Week of {datetime.now().strftime('%Y-%m-%d')}

## Revenue Summary
_Add revenue data from Accounting/_

## Task Completion
_Add task statistics_

## Goals Progress
_Review Business_Goals.md_

## Recommendations
_Add AI-generated recommendations_

---
*Generated by AI Employee Orchestrator v0.1*
'''
        
        audit_file.write_text(content, encoding='utf-8')
    
    def _process_all_actions(self):
        """Process all action files"""
        self.logger.info("Processing all actions")
        
        # Run plan generator
        from plan_generator import PlanGenerator
        generator = PlanGenerator(str(self.vault_path))
        plans = generator.process_all_actions()
        
        self.logger.info(f"Created {len(plans)} plans")
    
    def trigger_qwen(self, prompt: str, plan_file: Path = None) -> bool:
        """
        Trigger Qwen Code to process a prompt
        
        Args:
            prompt: The prompt to send to Qwen
            plan_file: Optional plan file to work on
        
        Returns:
            True if Qwen was triggered successfully
        """
        self.logger.info("Triggering Qwen Code CLI")
        
        # Build Qwen command
        cmd = ['qwen']
        
        # Add model if specified
        if self.qwen_model:
            cmd.extend(['--model', self.qwen_model])
        
        # Add prompt
        cmd.extend(['-p', prompt])
        
        # Add plan file context if provided
        if plan_file and plan_file.exists():
            cmd.append(str(plan_file))
        
        try:
            # Run Qwen Code
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            # For now, just log that Qwen should be triggered
            # In production, you'd integrate with Qwen Code API
            self.logger.info("Qwen Code CLI triggered (would run interactively)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error triggering Qwen: {e}")
            return False
    
    def trigger_claude(self, prompt: str, plan_file: Path = None) -> bool:
        """
        Trigger Claude Code to process a prompt (fallback)
        
        Args:
            prompt: The prompt to send to Claude
            plan_file: Optional plan file to work on
        
        Returns:
            True if Claude was triggered successfully
        """
        self.logger.info("Triggering Claude Code (fallback)")
        
        # Build Claude command
        cmd = ['claude']
        
        # Add model if specified
        if self.claude_model:
            cmd.extend(['--model', self.claude_model])
        
        # Add prompt
        cmd.extend(['-p', prompt])
        
        # Add plan file context if provided
        if plan_file and plan_file.exists():
            cmd.append(str(plan_file))
        
        try:
            # Run Claude (this will be interactive)
            # For non-interactive, we'd use a different approach
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            # For now, just log that Claude should be triggered
            # In production, you'd integrate with Claude Code API
            self.logger.info("Claude Code triggered (would run interactively)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error triggering Claude: {e}")
            return False
    
    def start_watchers(self):
        """Start all watcher scripts in background threads"""
        self.logger.info("Starting watcher scripts")
        
        watchers = [
            ('gmail_watcher.py', 'Gmail Watcher'),
            ('whatsapp_watcher.py', 'WhatsApp Watcher'),
        ]
        
        for watcher_file, name in watchers:
            watcher_path = self.vault_path / 'src' / watcher_file
            
            if watcher_path.exists():
                thread = threading.Thread(
                    target=self._run_watcher,
                    args=(watcher_path, name),
                    daemon=True
                )
                thread.start()
                self.watcher_threads.append(thread)
                self.logger.info(f"Started {name}")
            else:
                self.logger.warning(f"Watcher not found: {watcher_path}")
    
    def _run_watcher(self, watcher_path: Path, name: str):
        """Run a watcher script"""
        try:
            # Run the watcher
            subprocess.run(
                [sys.executable, str(watcher_path), str(self.vault_path)],
                cwd=str(watcher_path.parent)
            )
        except Exception as e:
            self.logger.error(f"{name} error: {e}")
    
    def run(self, once: bool = False):
        """
        Run the orchestrator
        
        Args:
            once: If True, run once and exit. If False, run continuously.
        """
        self.logger.info("Starting Personal AI Employee Orchestrator")
        self.logger.info(f"Vault: {self.vault_path}")
        self.logger.info(f"Check interval: {self.check_interval}s")
        
        # Setup scheduled tasks
        self._setup_scheduled_tasks()
        
        try:
            if once:
                # Run once and exit
                self.logger.info("Running in once mode")
                self.check_scheduled_tasks()
                self._process_all_actions()
            else:
                # Run continuously
                self.logger.info("Running in continuous mode")
                
                # Start watchers
                self.start_watchers()
                
                # Main loop
                while not self.stop_flag:
                    # Check scheduled tasks
                    self.check_scheduled_tasks()
                    
                    # Check for new actions to process
                    self._check_and_process_actions()
                    
                    # Wait before next cycle
                    time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            self.logger.info("Orchestrator stopped by user")
            self.stop_flag = True
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}")
            raise
    
    def _setup_scheduled_tasks(self):
        """Setup default scheduled tasks"""
        # Daily briefing at 8:00 AM
        self.add_scheduled_task({
            'name': 'Daily Briefing',
            'type': 'daily_briefing',
            'schedule': {'time': '08:00'},
        })
        
        # Weekly audit on Monday at 9:00 AM
        self.add_scheduled_task({
            'name': 'Weekly Audit',
            'type': 'weekly_audit',
            'schedule': {'time': '09:00'},
        })
        
        # Process actions every 5 minutes
        self.add_scheduled_task({
            'name': 'Process Actions',
            'type': 'process_actions',
            'schedule': {'interval': 300},
        })
    
    def _check_and_process_actions(self):
        """Check for new actions and process them"""
        action_files = list(self.needs_action.glob('*.md'))
        
        if action_files:
            self.logger.info(f"Found {len(action_files)} action files")
            self._process_all_actions()


def load_config(config_path: str = None) -> Dict:
    """Load configuration from file"""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Personal AI Employee Orchestrator')
    parser.add_argument('--vault', type=str, help='Path to vault folder')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--config', type=str, help='Path to config file')
    args = parser.parse_args()
    
    # Get vault path
    if args.vault:
        vault_path = args.vault
    else:
        vault_path = Path(__file__).parent.parent
    
    # Load config
    config = load_config(args.config)
    
    print("=" * 60)
    print("Personal AI Employee - Silver Tier Orchestrator")
    print("=" * 60)
    print(f"\nVault: {vault_path}")
    print(f"Mode: {'Once' if args.once else 'Continuous'}")
    print("\nPress Ctrl+C to stop\n")
    
    # Create and run orchestrator
    orchestrator = Orchestrator(str(vault_path), config)
    orchestrator.run(once=args.once)
