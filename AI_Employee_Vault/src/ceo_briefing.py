"""
CEO Briefing Generator - Weekly Business and Accounting Audit
Part of Personal AI Employee Gold Tier

Generates comprehensive weekly briefings including:
- Revenue summary
- Task completion stats
- Goals progress
- Bottlenecks identified
- Proactive suggestions
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CEOBriefingGenerator:
    """
    Generates weekly CEO briefings from vault data.
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.briefings_folder = self.vault_path / 'Briefings'
        self.accounting_folder = self.vault_path / 'Accounting'
        self.done_folder = self.vault_path / 'Done'
        self.logs_folder = self.vault_path / 'Logs'
        self.business_goals_file = self.vault_path / 'Business_Goals.md'
        
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def generate_weekly_briefing(
        self,
        week_start: datetime = None,
        output_file: str = None
    ) -> Path:
        """
        Generate weekly CEO briefing
        
        Args:
            week_start: Start of week (default: last Monday)
            output_file: Custom output filename
        
        Returns:
            Path to generated briefing
        """
        if week_start is None:
            # Default to last Monday
            today = datetime.now()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday, weeks=1)
        
        week_end = week_start + timedelta(days=6)  # Sunday
        
        # Collect data
        revenue_data = self._collect_revenue_data(week_start, week_end)
        task_data = self._collect_task_data(week_start, week_end)
        goals_data = self._collect_goals_data()
        bottlenecks = self._identify_bottlenecks(task_data)
        suggestions = self._generate_suggestions(revenue_data, task_data, goals_data)
        
        # Generate briefing
        briefing_date = week_start.strftime('%Y-%m-%d')
        if output_file is None:
            output_file = f"Weekly_CEO_Briefing_{briefing_date}.md"
        
        briefing_path = self.briefings_folder / output_file
        
        content = self._format_briefing(
            week_start=week_start,
            week_end=week_end,
            revenue=revenue_data,
            tasks=task_data,
            goals=goals_data,
            bottlenecks=bottlenecks,
            suggestions=suggestions
        )
        
        briefing_path.write_text(content, encoding='utf-8')
        self.logger.info(f"Generated weekly briefing: {briefing_path}")
        
        return briefing_path
    
    def _collect_revenue_data(
        self,
        week_start: datetime,
        week_end: datetime
    ) -> Dict:
        """Collect revenue data from accounting folder"""
        revenue = {
            'total': 0,
            'invoices_sent': 0,
            'invoices_paid': 0,
            'pending': 0,
            'by_source': {},
            'transactions': [],
        }
        
        # Look for accounting files
        for accounting_file in self.accounting_folder.glob('*.md'):
            content = accounting_file.read_text(encoding='utf-8')
            
            # Extract transactions (simple regex parsing)
            # In production, would use structured data
            transaction_matches = re.findall(
                r'(\d{4}-\d{2}-\d{2}).*?\$(\d+\.?\d*)',
                content
            )
            
            for date_str, amount in transaction_matches:
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d')
                    if week_start <= date <= week_end:
                        amount_float = float(amount)
                        revenue['total'] += amount_float
                        revenue['transactions'].append({
                            'date': date_str,
                            'amount': amount,
                        })
                except ValueError:
                    continue
        
        # Count invoices
        invoices_folder = self.vault_path / 'Invoices'
        if invoices_folder.exists():
            for invoice_file in invoices_folder.glob('*.md'):
                content = invoice_file.read_text(encoding='utf-8')
                if 'status: paid' in content.lower():
                    revenue['invoices_paid'] += 1
                elif 'status: sent' in content.lower():
                    revenue['invoices_sent'] += 1
                elif 'status: pending' in content.lower():
                    revenue['pending'] += 1
        
        revenue['total'] = round(revenue['total'], 2)
        
        return revenue
    
    def _collect_task_data(
        self,
        week_start: datetime,
        week_end: datetime
    ) -> Dict:
        """Collect task completion data"""
        tasks = {
            'completed': 0,
            'pending': 0,
            'failed': 0,
            'by_type': {},
            'avg_completion_time': 0,
            'completion_times': [],
        }
        
        # Count completed tasks
        for done_file in self.done_folder.glob('*.md'):
            try:
                mtime = datetime.fromtimestamp(done_file.stat().st_mtime)
                if week_start <= mtime <= week_end:
                    tasks['completed'] += 1
                    
                    # Extract type from content
                    content = done_file.read_text(encoding='utf-8')
                    type_match = re.search(r'type:\s*(\w+)', content)
                    if type_match:
                        task_type = type_match.group(1)
                        tasks['by_type'][task_type] = \
                            tasks['by_type'].get(task_type, 0) + 1
            except Exception:
                continue
        
        # Count pending tasks
        needs_action = self.vault_path / 'Needs_Action'
        if needs_action.exists():
            tasks['pending'] = len(list(needs_action.glob('*.md')))
        
        # Count failed tasks
        failed_folder = self.vault_path / 'Failed'
        if failed_folder.exists():
            tasks['failed'] = len(list(failed_folder.glob('*.md')))
        
        return tasks
    
    def _collect_goals_data(self) -> Dict:
        """Collect goals progress from Business_Goals.md"""
        goals = {
            'objectives': [],
            'metrics': [],
            'progress': [],
        }
        
        if not self.business_goals_file.exists():
            return goals
        
        content = self.business_goals_file.read_text(encoding='utf-8')
        
        # Extract objectives
        objectives = re.findall(r'^#\s+(.+)$', content, re.MULTILINE)
        goals['objectives'] = objectives[:5]  # Top 5 objectives
        
        # Extract metrics table
        metrics_match = re.search(
            r'\| Metric \|.*?\|.*?\|.*?\|([\s\S]*?)(?=\n\n|\Z)',
            content
        )
        if metrics_match:
            goals['metrics_text'] = metrics_match.group(1)
        
        return goals
    
    def _identify_bottlenecks(self, task_data: Dict) -> List[Dict]:
        """Identify bottlenecks from task data"""
        bottlenecks = []
        
        # Check for high pending count
        if task_data['pending'] > 10:
            bottlenecks.append({
                'type': 'high_pending_tasks',
                'severity': 'high',
                'description': f"{task_data['pending']} tasks pending action",
                'recommendation': 'Review and prioritize pending tasks',
            })
        
        # Check for failed tasks
        if task_data['failed'] > 0:
            bottlenecks.append({
                'type': 'failed_tasks',
                'severity': 'critical',
                'description': f"{task_data['failed']} tasks failed",
                'recommendation': 'Review failed tasks in /Failed folder',
            })
        
        # Check for low completion rate
        total = task_data['completed'] + task_data['pending']
        if total > 0:
            completion_rate = task_data['completed'] / total
            if completion_rate < 0.5:
                bottlenecks.append({
                    'type': 'low_completion_rate',
                    'severity': 'medium',
                    'description': f'Completion rate: {completion_rate:.0%}',
                    'recommendation': 'Increase task processing frequency',
                })
        
        return bottlenecks
    
    def _generate_suggestions(
        self,
        revenue: Dict,
        tasks: Dict,
        goals: Dict
    ) -> List[Dict]:
        """Generate proactive suggestions"""
        suggestions = []
        
        # Revenue-based suggestions
        if revenue['total'] < 1000:  # Example threshold
            suggestions.append({
                'category': 'revenue',
                'priority': 'high',
                'suggestion': 'Revenue below target - consider outreach campaign',
                'action': 'Create LinkedIn post about services',
            })
        
        # Invoice follow-up
        if revenue['pending'] > 3:
            suggestions.append({
                'category': 'accounts_receivable',
                'priority': 'medium',
                'suggestion': f"{revenue['pending']} invoices pending payment",
                'action': 'Send payment reminder emails',
            })
        
        # Task automation
        if tasks['completed'] > 20:
            suggestions.append({
                'category': 'efficiency',
                'priority': 'low',
                'suggestion': 'High task volume - consider automation',
                'action': 'Review repetitive tasks for automation opportunities',
            })
        
        return suggestions
    
    def _format_briefing(
        self,
        week_start: datetime,
        week_end: datetime,
        revenue: Dict,
        tasks: Dict,
        goals: Dict,
        bottlenecks: List[Dict],
        suggestions: List[Dict]
    ) -> str:
        """Format the briefing document"""
        week_num = week_start.isocalendar()[1]
        year = week_start.year
        
        content = f'''---
generated: {datetime.now().isoformat()}
period: {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}
week: {week_num}
year: {year}
type: weekly_ceo_briefing
---

# Weekly CEO Briefing

**Week {week_num}, {year}**  
**Period:** {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}

---

## Executive Summary

{self._generate_executive_summary(revenue, tasks, bottlenecks)}

---

## Revenue Summary

| Metric | Value |
|--------|-------|
| **Total Revenue** | ${revenue['total']:,.2f} |
| Invoices Paid | {revenue['invoices_paid']} |
| Invoices Pending | {revenue['pending']} |
| Transactions | {len(revenue['transactions'])} |

### Revenue Trend
{self._format_revenue_trend(revenue)}

---

## Task Completion

| Metric | Count |
|--------|-------|
| **Completed** | {tasks['completed']} |
| Pending | {tasks['pending']} |
| Failed | {tasks['failed']} |

### By Type
{self._format_task_by_type(tasks)}

---

## Goals Progress

{self._format_goals_progress(goals)}

---

## Bottlenecks Identified

{self._format_bottlenecks(bottlenecks)}

---

## Proactive Suggestions

{self._format_suggestions(suggestions)}

---

## Upcoming Deadlines

{self._get_upcoming_deadlines()}

---

## Notes

_Add additional notes and context here_

---

*Generated by AI Employee CEO Briefing Generator v0.1*
'''
        
        return content
    
    def _generate_executive_summary(
        self,
        revenue: Dict,
        tasks: Dict,
        bottlenecks: List[Dict]
    ) -> str:
        """Generate executive summary text"""
        summary_parts = []
        
        # Revenue status
        if revenue['total'] > 5000:
            summary_parts.append("Strong revenue week.")
        elif revenue['total'] > 1000:
            summary_parts.append("Moderate revenue generation.")
        else:
            summary_parts.append("Revenue needs attention.")
        
        # Task status
        if tasks['completed'] > 10:
            summary_parts.append(f"High productivity with {tasks['completed']} tasks completed.")
        else:
            summary_parts.append(f"{tasks['completed']} tasks completed this week.")
        
        # Bottlenecks
        critical = [b for b in bottlenecks if b.get('severity') == 'critical']
        if critical:
            summary_parts.append(f"⚠️ {len(critical)} critical issue(s) require attention.")
        
        return " ".join(summary_parts)
    
    def _format_revenue_trend(self, revenue: Dict) -> str:
        """Format revenue trend section"""
        if not revenue['transactions']:
            return "_No transactions recorded this week._"
        
        # Simple trend calculation
        transactions = revenue['transactions']
        if len(transactions) >= 2:
            first_half = sum(float(t['amount']) for t in transactions[:len(transactions)//2])
            second_half = sum(float(t['amount']) for t in transactions[len(transactions)//2:])
            
            if second_half > first_half:
                return "📈 Trending upward (more revenue in second half of week)"
            elif second_half < first_half:
                return "📉 Trending downward (more revenue in first half of week)"
            else:
                return "➡️ Stable revenue throughout the week"
        
        return "_Insufficient data for trend analysis_"
    
    def _format_task_by_type(self, tasks: Dict) -> str:
        """Format task breakdown by type"""
        if not tasks['by_type']:
            return "_No task type data available_"
        
        lines = []
        for task_type, count in sorted(tasks['by_type'].items(), key=lambda x: -x[1]):
            lines.append(f"- {task_type.replace('_', ' ').title()}: {count}")
        
        return '\n'.join(lines)
    
    def _format_goals_progress(self, goals: Dict) -> str:
        """Format goals progress section"""
        if not goals['objectives']:
            return "_No goals defined. Update Business_Goals.md_"
        
        lines = ["### Key Objectives"]
        for i, obj in enumerate(goals['objectives'][:5], 1):
            lines.append(f"{i}. {obj}")
        
        return '\n'.join(lines)
    
    def _format_bottlenecks(self, bottlenecks: List[Dict]) -> str:
        """Format bottlenecks section"""
        if not bottlenecks:
            return "✅ No significant bottlenecks identified."
        
        lines = []
        for bottleneck in bottlenecks:
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(
                bottleneck.get('severity', 'low'), '⚪'
            )
            lines.append(f"- {emoji} **{bottleneck['type']}**: {bottleneck['description']}")
            lines.append(f"  - Action: {bottleneck['recommendation']}")
        
        return '\n'.join(lines)
    
    def _format_suggestions(self, suggestions: List[Dict]) -> str:
        """Format suggestions section"""
        if not suggestions:
            return "_No suggestions at this time._"
        
        lines = []
        for suggestion in suggestions:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(
                suggestion.get('priority', 'low'), '⚪'
            )
            lines.append(f"- {priority_emoji} [{suggestion['category']}] {suggestion['suggestion']}")
            lines.append(f"  - Action: {suggestion['action']}")
        
        return '\n'.join(lines)
    
    def _get_upcoming_deadlines(self) -> str:
        """Get upcoming deadlines"""
        # This would integrate with calendar/task system
        # For now, return placeholder
        return "_No upcoming deadlines tracked. Add to Business_Goals.md_"


if __name__ == '__main__':
    import sys
    
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent
    
    print("=" * 60)
    print("CEO Briefing Generator - Personal AI Employee")
    print("=" * 60)
    
    generator = CEOBriefingGenerator(str(vault_path))
    
    # Generate briefing
    briefing_path = generator.generate_weekly_briefing()
    
    print(f"\n✅ Briefing generated: {briefing_path}")
    print(f"\nOpen in Obsidian to review: {briefing_path}")
