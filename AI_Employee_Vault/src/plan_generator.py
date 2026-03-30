"""
Plan Generator - Creates structured Plan.md files for Claude to execute
Part of Personal AI Employee Silver Tier

This module analyzes action files in Needs_Action and creates corresponding
Plan.md files with step-by-step tasks for Claude Code to execute.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re


class PlanGenerator:
    """Generates structured plans from action files"""
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.plans_folder = self.vault_path / 'Plans'
        self.needs_action = self.vault_path / 'Needs_Action'
        
        self.plans_folder.mkdir(parents=True, exist_ok=True)
        
        # Plan templates for different action types
        self.templates = {
            'email': self._email_plan_template,
            'whatsapp': self._whatsapp_plan_template,
            'file_drop': self._file_plan_template,
            'invoice': self._invoice_plan_template,
            'payment': self._payment_plan_template,
            'social_post': self._social_post_plan_template,
            'default': self._default_plan_template,
        }
    
    def analyze_action_file(self, action_file: Path) -> Dict:
        """Analyze an action file and extract metadata"""
        content = action_file.read_text(encoding='utf-8')
        
        # Extract frontmatter
        frontmatter = {}
        fm_match = re.search(r'---\n(.*?)\n---', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
        
        # Determine action type
        action_type = frontmatter.get('type', 'default')
        
        # Extract priority
        priority = frontmatter.get('priority', 'normal')
        
        return {
            'path': action_file,
            'type': action_type,
            'priority': priority,
            'frontmatter': frontmatter,
            'content': content,
        }
    
    def create_plan(self, action_info: Dict) -> Path:
        """Create a Plan.md file for the given action"""
        action_type = action_info['type']
        
        # Get appropriate template
        template_func = self.templates.get(action_type, self.templates['default'])
        plan_content = template_func(action_info)
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        action_name = action_info['path'].stem
        plan_filename = f'PLAN_{action_name}_{timestamp}.md'
        
        # Write plan file
        plan_path = self.plans_folder / plan_filename
        plan_path.write_text(plan_content, encoding='utf-8')
        
        return plan_path
    
    def process_all_actions(self) -> List[Path]:
        """Process all action files in Needs_Action folder"""
        created_plans = []
        
        for action_file in self.needs_action.glob('*.md'):
            try:
                action_info = self.analyze_action_file(action_file)
                plan_path = self.create_plan(action_info)
                created_plans.append(plan_path)
                print(f"✓ Created plan: {plan_path.name}")
            except Exception as e:
                print(f"✗ Error processing {action_file.name}: {e}")
        
        return created_plans
    
    # ========== Plan Templates ==========
    
    def _email_plan_template(self, action: Dict) -> str:
        """Generate plan for email action"""
        fm = action['frontmatter']
        return f'''---
type: email_plan
status: pending
created: {datetime.now().isoformat()}
priority: {fm.get('priority', 'normal')}
source: {action['path'].name}
assignee: claude_code
---

# Email Action Plan

## Context
- **From:** {fm.get('from', 'Unknown')}
- **Subject:** {fm.get('subject', 'No Subject')}
- **Priority:** {fm.get('priority', 'normal')}
- **Received:** {fm.get('received', 'Unknown')}

## Objectives
1. Read and understand the email content
2. Determine required response/action
3. Execute appropriate response
4. Document outcome

## Steps

### Step 1: Analyze Email Content
- [ ] Read the full email content in the source file
- [ ] Identify the sender's request/intent
- [ ] Check if response is needed
- [ ] Determine urgency level

### Step 2: Research & Context
- [ ] Check Company_Handbook.md for relevant policies
- [ ] Search for previous communications with sender
- [ ] Gather any needed information

### Step 3: Draft Response (if needed)
- [ ] Draft a professional response
- [ ] Include all necessary information
- [ ] Create approval file in /Pending_Approval if sending required

### Step 4: Take Action
- [ ] Send email (after approval) OR
- [ ] File/archive the email OR
- [ ] Create follow-up task

### Step 5: Document & Close
- [ ] Update this plan with actions taken
- [ ] Move source file to /Done folder
- [ ] Log action in Logs/

## Notes
_Add any observations or context here_

## Completion Status
- [ ] All steps completed
- [ ] Source file moved to /Done
- [ ] Logs updated

---
*Generated by AI Employee Plan Generator v0.1*
'''
    
    def _whatsapp_plan_template(self, action: Dict) -> str:
        """Generate plan for WhatsApp message"""
        fm = action['frontmatter']
        return f'''---
type: whatsapp_plan
status: pending
created: {datetime.now().isoformat()}
priority: {fm.get('priority', 'normal')}
source: {action['path'].name}
assignee: claude_code
---

# WhatsApp Message Plan

## Context
- **From:** {fm.get('chat_name', 'Unknown')}
- **Priority:** {fm.get('priority', 'normal')}
- **Received:** {fm.get('received', 'Unknown')}

## Objectives
1. Understand the WhatsApp message
2. Determine if response is needed
3. Draft appropriate response
4. Get approval and send

## Steps

### Step 1: Analyze Message
- [ ] Read the message content
- [ ] Identify urgency level
- [ ] Check for keywords: invoice, payment, urgent, help

### Step 2: Determine Response Strategy
- [ ] Is this a customer/client inquiry?
- [ ] Does it require immediate attention?
- [ ] Can it be automated or needs human input?

### Step 3: Draft Response
- [ ] Write a friendly, professional response
- [ ] Keep it concise (WhatsApp style)
- [ ] Address all points in the original message

### Step 4: Approval & Send
- [ ] Create approval file in /Pending_Approval
- [ ] Wait for human approval
- [ ] Send via WhatsApp (after approval)

### Step 5: Follow-up
- [ ] Set reminder if follow-up needed
- [ ] Document conversation outcome
- [ ] Move to /Done folder

## Response Draft
_Write your response here_

## Notes
_Add context or follow-up items_

## Completion Status
- [ ] All steps completed
- [ ] Source file moved to /Done

---
*Generated by AI Employee Plan Generator v0.1*
'''
    
    def _file_plan_template(self, action: Dict) -> str:
        """Generate plan for file drop action"""
        fm = action['frontmatter']
        return f'''---
type: file_plan
status: pending
created: {datetime.now().isoformat()}
source: {action['path'].name}
assignee: claude_code
---

# File Processing Plan

## Context
- **Original File:** {fm.get('original_name', 'Unknown')}
- **Size:** {fm.get('size', 'Unknown')} bytes
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Objectives
1. Understand what processing is needed
2. Execute the required actions
3. Document outcomes

## Steps

### Step 1: Analyze File
- [ ] Identify file type and content
- [ ] Determine what action is needed
- [ ] Check for any instructions

### Step 2: Process File
- [ ] Execute required processing
- [ ] Transform/convert if needed
- [ ] Generate any outputs

### Step 3: Store Results
- [ ] Save processed file to appropriate location
- [ ] Update Dashboard.md if needed
- [ ] Log the action

### Step 4: Cleanup
- [ ] Move source file to /Done
- [ ] Archive any outputs

## Notes
_Add observations here_

## Completion Status
- [ ] Processing complete
- [ ] Files archived
- [ ] Source moved to /Done

---
*Generated by AI Employee Plan Generator v0.1*
'''
    
    def _invoice_plan_template(self, action: Dict) -> str:
        """Generate plan for invoice-related action"""
        return f'''---
type: invoice_plan
status: pending
created: {datetime.now().isoformat()}
priority: high
assignee: claude_code
---

# Invoice Processing Plan

## Objectives
1. Generate/send invoice
2. Track payment
3. Update accounting

## Steps

### Step 1: Gather Invoice Details
- [ ] Identify client/customer
- [ ] Determine products/services
- [ ] Calculate amounts
- [ ] Apply taxes/discounts

### Step 2: Create Invoice
- [ ] Generate invoice document
- [ ] Save to /Invoices folder
- [ ] Log in Accounting/

### Step 3: Send Invoice
- [ ] Draft email with invoice
- [ ] Create approval file
- [ ] Send after approval

### Step 4: Track Payment
- [ ] Set payment reminder date
- [ ] Monitor for payment
- [ ] Update status when paid

## Notes
_Add details here_

---
*Generated by AI Employee Plan Generator v0.1*
'''
    
    def _payment_plan_template(self, action: Dict) -> str:
        """Generate plan for payment action"""
        return f'''---
type: payment_plan
status: pending
created: {datetime.now().isoformat()}
priority: high
assignee: claude_code
---

# Payment Processing Plan

⚠️ **REQUIRES HUMAN APPROVAL**

## Steps

### Step 1: Verify Payment Details
- [ ] Confirm payee information
- [ ] Verify amount
- [ ] Check invoice/reference
- [ ] Validate business purpose

### Step 2: Create Approval Request
- [ ] Create file in /Pending_Approval
- [ ] Include all payment details
- [ ] Wait for human approval

### Step 3: Execute Payment (After Approval)
- [ ] Access payment system
- [ ] Enter payment details
- [ ] Complete transaction
- [ ] Save confirmation

### Step 4: Record Transaction
- [ ] Update Accounting/
- [ ] Log in Logs/
- [ ] File receipts/documentation

## Notes
_Add details here_

---
*Generated by AI Employee Plan Generator v0.1*
'''
    
    def _social_post_plan_template(self, action: Dict) -> str:
        """Generate plan for social media post"""
        return f'''---
type: social_post_plan
status: pending
created: {datetime.now().isoformat()}
assignee: claude_code
---

# Social Media Post Plan

## Steps

### Step 1: Content Creation
- [ ] Draft post content
- [ ] Include relevant hashtags
- [ ] Check character limits
- [ ] Review for tone/accuracy

### Step 2: Approval
- [ ] Create approval file
- [ ] Wait for human review

### Step 3: Publish
- [ ] Post to LinkedIn (after approval)
- [ ] Log in Logs/linkedin_posts.md
- [ ] Schedule follow-up if needed

## Draft Content
_Write post here_

## Completion
- [ ] Posted successfully
- [ ] Logged

---
*Generated by AI Employee Plan Generator v0.1*
'''
    
    def _default_plan_template(self, action: Dict) -> str:
        """Default plan template for unknown action types"""
        fm = action['frontmatter']
        return f'''---
type: general_plan
status: pending
created: {datetime.now().isoformat()}
priority: {fm.get('priority', 'normal')}
source: {action['path'].name}
assignee: claude_code
---

# Action Plan

## Context
- **Source:** {action['path'].name}
- **Type:** {fm.get('type', 'unknown')}
- **Priority:** {fm.get('priority', 'normal')}

## Steps

### Step 1: Analyze
- [ ] Read and understand the request
- [ ] Identify required actions
- [ ] Check for dependencies

### Step 2: Plan
- [ ] Break down into subtasks
- [ ] Identify resources needed
- [ ] Estimate time required

### Step 3: Execute
- [ ] Complete subtasks
- [ ] Document progress
- [ ] Handle any issues

### Step 4: Complete
- [ ] Verify all work done
- [ ] Update relevant files
- [ ] Move source to /Done

## Notes
_Add details here_

## Completion Status
- [ ] All tasks complete
- [ ] Documentation updated
- [ ] Source filed

---
*Generated by AI Employee Plan Generator v0.1*
'''


if __name__ == '__main__':
    import sys
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    print(f"Processing actions in: {vault_path}")
    
    generator = PlanGenerator(str(vault_path))
    plans = generator.process_all_actions()
    
    print(f"\n✓ Created {len(plans)} plan(s)")
