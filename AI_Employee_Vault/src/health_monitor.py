"""
Health Monitoring System - Platinum Tier
Part of Personal AI Employee Platinum Tier

Monitors Cloud Agent and Local Executive health.
Auto-restarts failed processes.
Generates health reports.
"""

import os
import sys
import time
import json
import logging
import subprocess
import psutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class HealthMonitor:
    """
    Monitors health of all AI Employee components.
    
    Features:
    - Heartbeat monitoring
    - Process monitoring
    - Auto-restart on failure
    - Health reports
    - Alert generation
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Health files
        self.health_folder = self.vault_path / '.health'
        self.health_folder.mkdir(parents=True, exist_ok=True)
        
        self.cloud_health_file = self.health_folder / 'cloud_health.json'
        self.local_health_file = self.health_folder / 'local_health.json'
        
        # Process tracking
        self.process_file = self.health_folder / 'processes.json'
        self.processes: Dict[str, subprocess.Popen] = {}
        
        # Configuration
        self.heartbeat_timeout = 300  # 5 minutes
        self.max_restarts = 3
        self.restart_count: Dict[str, int] = {}
        self.last_restart: Dict[str, datetime] = {}
        
        # Load process state
        self._load_processes()
    
    def _load_processes(self):
        """Load process state"""
        if self.process_file.exists():
            try:
                with open(self.process_file, 'r') as f:
                    data = json.load(f)
                self.restart_count = data.get('restart_count', {})
                self.last_restart = {
                    k: datetime.fromisoformat(v)
                    for k, v in data.get('last_restart', {}).items()
                }
            except:
                pass
    
    def _save_processes(self):
        """Save process state"""
        data = {
            'restart_count': self.restart_count,
            'last_restart': {
                k: v.isoformat() for k, v in self.last_restart.items()
            },
        }
        with open(self.process_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def check_cloud_health(self) -> Dict:
        """Check cloud agent health"""
        health = {
            'agent': 'cloud',
            'status': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'issues': [],
        }
        
        # Check health file
        if self.cloud_health_file.exists():
            try:
                with open(self.cloud_health_file, 'r') as f:
                    cloud_health = json.load(f)
                
                last_heartbeat = datetime.fromisoformat(cloud_health['timestamp'])
                age = datetime.now() - last_heartbeat
                
                if age < timedelta(seconds=self.heartbeat_timeout):
                    health['status'] = cloud_health.get('status', 'healthy')
                    health['uptime'] = cloud_health.get('uptime_seconds', 0)
                    health['processed_tasks'] = cloud_health.get('processed_tasks', 0)
                else:
                    health['status'] = 'unhealthy'
                    health['issues'].append(f'Heartbeat stale: {age.seconds}s old')
            except Exception as e:
                health['status'] = 'error'
                health['issues'].append(str(e))
        else:
            health['status'] = 'no_data'
            health['issues'].append('No health file found')
        
        return health
    
    def check_local_health(self) -> Dict:
        """Check local executive health"""
        health = {
            'agent': 'local',
            'status': 'unknown',
            'timestamp': datetime.now().isoformat(),
            'issues': [],
        }
        
        # Check if local processes are running
        local_running = self._check_process_running('local_executive')
        health['process_running'] = local_running
        
        if local_running:
            health['status'] = 'healthy'
        else:
            health['status'] = 'unhealthy'
            health['issues'].append('Local Executive not running')
        
        return health
    
    def _check_process_running(self, process_name: str) -> bool:
        """Check if process is running"""
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', []) or []
                cmd_str = ' '.join(cmdline)
                if process_name in cmd_str:
                    return True
            except:
                pass
        return False
    
    def start_cloud_agent(self) -> Optional[subprocess.Popen]:
        """Start cloud agent process"""
        self.logger.info("Starting Cloud Agent")
        
        try:
            # In production, would start on cloud VM
            # For local testing:
            process = subprocess.Popen(
                [sys.executable, str(self.vault_path / 'src' / 'cloud_agent.py'), '--once'],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            self.processes['cloud'] = process
            self.logger.info(f"Cloud Agent started: PID {process.pid}")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start Cloud Agent: {e}")
            return None
    
    def start_local_executive(self) -> Optional[subprocess.Popen]:
        """Start local executive process"""
        self.logger.info("Starting Local Executive")
        
        try:
            process = subprocess.Popen(
                [sys.executable, str(self.vault_path / 'src' / 'local_executive.py'), '--once'],
                cwd=str(self.vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            
            self.processes['local'] = process
            self.logger.info(f"Local Executive started: PID {process.pid}")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start Local Executive: {e}")
            return None
    
    def check_and_restart(self, agent: str) -> bool:
        """Check if agent needs restart and restart if needed"""
        if agent == 'cloud':
            health = self.check_cloud_health()
        else:
            health = self.check_local_health()
        
        needs_restart = health['status'] in ['unhealthy', 'error', 'no_data']
        
        if needs_restart:
            # Check restart limits
            recent_restarts = 0
            cutoff = datetime.now() - timedelta(hours=1)
            for restart_time in self.last_restart.values():
                if restart_time > cutoff:
                    recent_restarts += 1
            
            if recent_restarts >= self.max_restarts:
                self.logger.warning(f"Max restarts reached for {agent}")
                self._alert_max_restarts(agent)
                return False
            
            # Restart
            self.logger.info(f"Restarting {agent}")
            self.restart_count[agent] = self.restart_count.get(agent, 0) + 1
            self.last_restart[agent] = datetime.now()
            self._save_processes()
            
            if agent == 'cloud':
                return self.start_cloud_agent() is not None
            else:
                return self.start_local_executive() is not None
        
        return True
    
    def _alert_max_restarts(self, agent: str):
        """Alert about max restarts reached"""
        alert_file = self.vault_path / 'Errors' / f"MAX_RESTARTS_{agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        content = f"""---
type: max_restarts_alert
created: {datetime.now().isoformat()}
agent: {agent}
severity: critical
---

# Maximum Restarts Reached

**Agent:** {agent}  
**Time:** {datetime.now().isoformat()}  
**Restarts in last hour:** {self.restart_count.get(agent, 0)}

---
**Action Required:** Manual intervention needed
"""
        
        alert_file.write_text(content)
        self.logger.critical(f"Max restarts alert: {agent}")
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        cloud_health = self.check_cloud_health()
        local_health = self.check_local_health()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'cloud': cloud_health,
            'local': local_health,
            'restarts': self.restart_count,
            'status': 'healthy' if (
                cloud_health['status'] == 'healthy' and
                local_health['status'] == 'healthy'
            ) else 'degraded',
        }
        
        # Save report
        report_file = self.health_folder / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_monitoring(self, once: bool = False):
        """Run health monitoring loop"""
        self.logger.info("Starting Health Monitor")
        
        try:
            while True:
                # Check health
                cloud_ok = self.check_and_restart('cloud')
                local_ok = self.check_and_restart('local')
                
                if not cloud_ok or not local_ok:
                    self.logger.warning(f"Health issues detected: cloud={cloud_ok}, local={local_ok}")
                
                # Generate report every 5 minutes
                self.generate_health_report()
                
                if once:
                    break
                
                time.sleep(60)  # Check every minute
        
        except KeyboardInterrupt:
            self.logger.info("Health Monitor stopped")


if __name__ == '__main__':
    vault_path = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent.parent)
    once = '--once' in sys.argv
    
    monitor = HealthMonitor(vault_path)
    
    if once:
        report = monitor.generate_health_report()
        print("Health Report:")
        print(json.dumps(report, indent=2))
    else:
        monitor.run_monitoring()
