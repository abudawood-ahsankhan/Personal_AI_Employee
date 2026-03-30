"""
Ralph Wiggum Loop - Autonomous Task Completion System
Part of Personal AI Employee Gold Tier

This implements the "Ralph Wiggum" pattern - a persistence loop that keeps
Claude Code working on a task until it's complete.

The pattern:
1. Create a task file with a prompt
2. Claude works on the task
3. Claude tries to exit
4. Stop hook checks: Is task complete?
5. If NO → Block exit, re-inject prompt (loop continues)
6. If YES → Allow exit

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
"""

import os
import time
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class RalphWiggumLoop:
    """
    Implements the Ralph Wiggum persistence pattern for autonomous task completion.
    """
    
    def __init__(
        self,
        vault_path: str,
        max_iterations: int = 10,
        claude_model: str = 'claude-sonnet-4-5-20250929'
    ):
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.claude_model = claude_model
        
        # Folders
        self.tasks_folder = self.vault_path / 'Tasks'
        self.in_progress_folder = self.vault_path / 'In_Progress'
        self.done_folder = self.vault_path / 'Done'
        
        # Ensure folders exist
        for folder in [self.tasks_folder, self.in_progress_folder, self.done_folder]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Task completion checkers (registered by task type)
        self.completion_checkers: Dict[str, Callable] = {}
        
        # Register default completion checkers
        self._register_default_checkers()
    
    def _register_default_checkers(self):
        """Register default completion checkers"""
        
        def check_file_moved_to_done(task: Dict) -> bool:
            """Check if task file was moved to Done folder"""
            done_file = self.done_folder / task.get('source_file', '')
            return done_file.exists()
        
        def check_promise_in_output(task: Dict) -> bool:
            """Check if Claude output contains completion promise"""
            output_file = self.in_progress_folder / f"{task.get('id')}_output.md"
            if output_file.exists():
                content = output_file.read_text()
                return '<promise>TASK_COMPLETE</promise>' in content or \
                       'TASK_COMPLETE' in content
            return False
        
        self.completion_checkers['file_movement'] = check_file_moved_to_done
        self.completion_checkers['promise'] = check_promise_in_output
    
    def create_task(
        self,
        prompt: str,
        task_type: str = 'general',
        priority: str = 'normal',
        context: Dict = None
    ) -> Dict:
        """
        Create a new task for Claude to work on
        
        Args:
            prompt: The task prompt for Claude
            task_type: Type of task (general, email, invoice, etc.)
            priority: Task priority (low, normal, high, critical)
            context: Additional context data
        
        Returns:
            Task dictionary
        """
        task_id = f"TASK_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = {
            'id': task_id,
            'type': task_type,
            'priority': priority,
            'prompt': prompt,
            'context': context or {},
            'status': 'pending',
            'created': datetime.now().isoformat(),
            'iterations': 0,
            'completion_criteria': ['file_movement', 'promise'],
        }
        
        # Save task file
        task_file = self.tasks_folder / f"{task_id}.json"
        with open(task_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        self.logger.info(f"Created task: {task_id}")
        return task
    
    def start_task(self, task: Dict) -> Path:
        """
        Move task to In_Progress and start Claude
        
        Args:
            task: Task dictionary
        
        Returns:
            Path to Claude output file
        """
        # Move to in progress
        task['status'] = 'in_progress'
        task['started'] = datetime.now().isoformat()
        
        in_progress_file = self.in_progress_folder / f"{task['id']}.json"
        with open(in_progress_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        # Remove from tasks folder
        tasks_file = self.tasks_folder / f"{task['id']}.json"
        if tasks_file.exists():
            tasks_file.unlink()
        
        return in_progress_file
    
    def run_claude(self, task: Dict, iteration: int = 0) -> str:
        """
        Run Claude Code on the task
        
        Args:
            task: Task dictionary
            iteration: Current iteration number
        
        Returns:
            Claude's output
        """
        self.logger.info(f"Running Claude (iteration {iteration + 1})")
        
        # Build Claude command
        cmd = ['claude']
        
        # Add model
        cmd.extend(['--model', self.claude_model])
        
        # Build prompt
        prompt = self._build_prompt(task, iteration)
        cmd.extend(['-p', prompt])
        
        try:
            # Run Claude
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.vault_path)
            )
            
            output = result.stdout + result.stderr
            
            # Save output
            output_file = self.in_progress_folder / f"{task['id']}_output_{iteration}.md"
            output_file.write_text(output, encoding='utf-8')
            
            return output
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Claude timed out on iteration {iteration + 1}")
            return "ERROR: Claude timed out"
        except Exception as e:
            self.logger.error(f"Error running Claude: {e}")
            return f"ERROR: {e}"
    
    def _build_prompt(self, task: Dict, iteration: int) -> str:
        """Build the prompt for Claude"""
        base_prompt = task['prompt']
        
        if iteration > 0:
            # Include previous output for context
            prev_output_file = self.in_progress_folder / f"{task['id']}_output_{iteration - 1}.md"
            if prev_output_file.exists():
                prev_output = prev_output_file.read_text()
                
                prompt = f"""
You are working on a task. Continue from where you left off.

PREVIOUS ATTEMPT OUTPUT:
{prev_output}

CURRENT TASK (still not complete):
{base_prompt}

INSTRUCTIONS:
- Review what was done in the previous attempt
- Identify what still needs to be done
- Continue working on the task
- If the task is complete, output: <promise>TASK_COMPLETE</promise>
- If you cannot complete the task, explain why and what's blocking you
"""
                return prompt.strip()
        
        return f"""
You are an autonomous AI employee. Complete the following task:

{base_prompt}

INSTRUCTIONS:
- Work through the task step by step
- Use the file system to read/write as needed
- When the task is complete, output: <promise>TASK_COMPLETE</promise>
- If you cannot complete the task, explain what's blocking you

CONTEXT:
{json.dumps(task.get('context', {}), indent=2)}
""".strip()
    
    def is_task_complete(self, task: Dict) -> bool:
        """
        Check if the task is complete
        
        Args:
            task: Task dictionary
        
        Returns:
            True if task is complete
        """
        for criteria in task.get('completion_criteria', []):
            checker = self.completion_checkers.get(criteria)
            if checker:
                try:
                    if checker(task):
                        self.logger.info(f"Task complete by criteria: {criteria}")
                        return True
                except Exception as e:
                    self.logger.error(f"Error checking completion: {e}")
        
        return False
    
    def complete_task(self, task: Dict, output: str):
        """
        Mark task as complete and move to Done folder
        
        Args:
            task: Task dictionary
            output: Final output from Claude
        """
        task['status'] = 'completed'
        task['completed'] = datetime.now().isoformat()
        task['final_output'] = output
        
        # Move to done
        done_file = self.done_folder / f"{task['id']}_complete.json"
        with open(done_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        # Clean up in_progress
        in_progress_file = self.in_progress_folder / f"{task['id']}.json"
        if in_progress_file.exists():
            in_progress_file.unlink()
        
        self.logger.info(f"Task completed: {task['id']}")
    
    def fail_task(self, task: Dict, reason: str):
        """
        Mark task as failed
        
        Args:
            task: Task dictionary
            reason: Reason for failure
        """
        task['status'] = 'failed'
        task['failed'] = datetime.now().isoformat()
        task['failure_reason'] = reason
        
        # Move to failed folder
        failed_folder = self.vault_path / 'Failed'
        failed_folder.mkdir(parents=True, exist_ok=True)
        
        failed_file = failed_folder / f"{task['id']}_failed.json"
        with open(failed_file, 'w') as f:
            json.dump(task, f, indent=2)
        
        # Clean up in_progress
        in_progress_file = self.in_progress_folder / f"{task['id']}.json"
        if in_progress_file.exists():
            in_progress_file.unlink()
        
        self.logger.warning(f"Task failed: {task['id']} - {reason}")
    
    def run_task(self, task: Dict) -> bool:
        """
        Run the full Ralph Wiggum loop for a task
        
        Args:
            task: Task dictionary
        
        Returns:
            True if task completed successfully
        """
        self.logger.info(f"Starting Ralph Wiggum loop for task: {task['id']}")
        
        # Start task
        self.start_task(task)
        
        iteration = 0
        while iteration < self.max_iterations:
            # Run Claude
            output = self.run_claude(task, iteration)
            
            # Check if complete
            if self.is_task_complete(task):
                self.complete_task(task, output)
                return True
            
            # Check for explicit failure
            if 'ERROR:' in output or 'CANNOT COMPLETE' in output.upper():
                self.fail_task(task, output[:500])
                return False
            
            iteration += 1
        
        # Max iterations reached
        self.fail_task(task, f"Max iterations ({self.max_iterations}) reached")
        return False
    
    def run_all_pending_tasks(self):
        """Process all pending tasks"""
        pending_tasks = list(self.tasks_folder.glob('*.json'))
        
        self.logger.info(f"Found {len(pending_tasks)} pending tasks")
        
        completed = 0
        failed = 0
        
        for task_file in pending_tasks:
            try:
                with open(task_file, 'r') as f:
                    task = json.load(f)
                
                if self.run_task(task):
                    completed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                self.logger.error(f"Error processing task {task_file.name}: {e}")
                failed += 1
        
        self.logger.info(f"Processed {completed + failed} tasks: {completed} completed, {failed} failed")
        return completed, failed


if __name__ == '__main__':
    import sys
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    print("=" * 60)
    print("Ralph Wiggum Loop - Personal AI Employee")
    print("=" * 60)
    print(f"\nVault: {vault_path}")
    print(f"Max iterations: 10")
    print("\nUsage:")
    print("  1. Create task files in Tasks/ folder")
    print("  2. Run: python ralph_wiggum.py")
    print("  3. Tasks will be processed automatically")
    print("\nPress Ctrl+C to stop\n")
    
    ralph = RalphWiggumLoop(str(vault_path))
    ralph.run_all_pending_tasks()
