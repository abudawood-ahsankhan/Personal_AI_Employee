"""
Test Script - Platinum Tier Verification
Part of Personal AI Employee Platinum Tier

Usage:
    python test_platinum_tier.py
"""

import sys
from pathlib import Path


def test_file_exists(filepath: Path) -> bool:
    exists = filepath.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {filepath.name}")
    return exists


def test_folder_exists(folderpath: Path) -> bool:
    exists = folderpath.exists() and folderpath.is_dir()
    status = "✓" if exists else "✗"
    print(f"  {status} {folderpath.name}/")
    return exists


def run_tests(vault_path: Path):
    print("=" * 60)
    print("Personal AI Employee - Platinum Tier Verification")
    print("=" * 60)
    print()
    
    results = {
        'Platinum Components': [],
        'Cloud/Local Separation': [],
        'Sync Folders': [],
        'Documentation': [],
    }
    
    # Test Platinum Components
    print("🌟 Platinum Tier Components:")
    platinum_files = [
        'vault_sync.py',
        'cloud_agent.py',
        'local_executive.py',
        'health_monitor.py',
        'a2a_messaging.py',
    ]
    
    for filename in platinum_files:
        results['Platinum Components'].append(
            test_file_exists(vault_path / 'src' / filename)
        )
    print()
    
    # Test Cloud/Local Separation
    print("🔄 Cloud/Local Separation:")
    separation = [
        ('Needs_Action', 'cloud'),
        ('Needs_Action', 'local'),
        ('Plans', 'cloud'),
        ('Plans', 'local'),
        ('Pending_Approval', 'cloud'),
        ('Pending_Approval', 'local'),
        ('In_Progress', 'cloud_agent'),
        ('In_Progress', 'local_exec'),
    ]
    
    for folder, subfolder in separation:
        results['Cloud/Local Separation'].append(
            test_folder_exists(vault_path / folder / subfolder)
        )
    print()
    
    # Test Sync Folders
    print("📡 Sync Folders:")
    sync_folders = [
        'Updates',
        'Signals',
        'Sync_Exclude',
        'Messages',
    ]
    
    for folder in sync_folders:
        results['Sync Folders'].append(
            test_folder_exists(vault_path / folder)
        )
    print()
    
    # Test Deployment
    print("🚀 Deployment:")
    deploy_files = [
        vault_path.parent / 'deploy_cloud.sh',
        vault_path.parent / '.gitignore',
    ]
    
    for filepath in deploy_files:
        results['Documentation'].append(
            test_file_exists(filepath)
        )
    print()
    
    # Summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total = 0
    passed = 0
    
    for category, results_list in results.items():
        if results_list:
            category_total = len(results_list)
            category_passed = sum(results_list)
            total += category_total
            passed += category_passed
            
            percentage = (category_passed / category_total * 100) if category_total > 0 else 0
            status = "✅" if percentage >= 80 else "⚠️"
            print(f"{status} {category}: {category_passed}/{category_total} ({percentage:.0f}%)")
    
    overall = (passed / total * 100) if total > 0 else 0
    print()
    print(f"Overall: {passed}/{total} ({overall:.0f}%)")
    
    if overall >= 90:
        print("\n✅ Platinum Tier installation complete!")
    elif overall >= 70:
        print("\n⚠️  Most components installed")
    else:
        print("\n❌ Several components missing")


if __name__ == '__main__':
    vault_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent
    run_tests(vault_path)
