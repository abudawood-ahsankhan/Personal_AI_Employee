"""
Test Script - Gold Tier Verification
Part of Personal AI Employee Gold Tier

Run this script to verify all Gold Tier components are installed.

Usage:
    python test_gold_tier.py
"""

import sys
from pathlib import Path


def test_file_exists(filepath: Path, required: bool = True) -> bool:
    """Test if a file exists"""
    exists = filepath.exists()
    status = "✓" if exists else "✗"
    req = "" if required else "(optional)"
    print(f"  {status} {filepath.name} {req}")
    if required and not exists:
        return False
    return True


def test_folder_exists(folderpath: Path) -> bool:
    """Test if a folder exists"""
    exists = folderpath.exists() and folderpath.is_dir()
    status = "✓" if exists else "✗"
    print(f"  {status} {folderpath.name}/")
    return exists


def run_tests(vault_path: Path):
    """Run all Gold Tier tests"""
    print("=" * 60)
    print("Personal AI Employee - Gold Tier Verification")
    print("=" * 60)
    print()
    
    results = {
        'Core Components': [],
        'MCP Servers': [],
        'Gold Tier Components': [],
        'Folders': [],
        'Documentation': [],
    }
    
    # Test Core Components
    print("📦 Core Components:")
    core_files = [
        'base_watcher.py',
        'gmail_watcher.py',
        'whatsapp_watcher.py',
        'linkedin_poster.py',
        'plan_generator.py',
        'approval_manager.py',
        'orchestrator.py',
    ]
    
    for filename in core_files:
        results['Core Components'].append(
            test_file_exists(vault_path / 'src' / filename)
        )
    print()
    
    # Test Gold Tier Components
    print("🌟 Gold Tier Components:")
    gold_files = [
        'ralph_wiggum.py',
        'error_recovery.py',
        'audit_logger.py',
        'ceo_briefing.py',
    ]
    
    for filename in gold_files:
        results['Gold Tier Components'].append(
            test_file_exists(vault_path / 'src' / filename)
        )
    print()
    
    # Test MCP Servers
    print("🔌 MCP Servers:")
    mcp_servers = [
        ('mcp-odoo', 'index.js'),
        ('mcp-facebook', 'index.js'),
        ('mcp-twitter', 'index.js'),
        ('mcp-email', 'index.js'),
        ('mcp-linkedin', 'index.js'),
    ]
    
    for server_dir, main_file in mcp_servers:
        server_path = vault_path / 'src' / server_dir
        exists = server_path.exists()
        has_main = (server_path / main_file).exists() if exists else False
        status = "✓" if has_main else "✗"
        print(f"  {status} {server_dir}/")
        results['MCP Servers'].append(has_main)
    print()
    
    # Test Folders
    print("📁 Gold Tier Folders:")
    gold_folders = [
        'In_Progress',
        'Tasks',
        'Failed',
        'Errors',
        'Quarantine',
        'Social',
        'Updates',
    ]
    
    for folder in gold_folders:
        results['Folders'].append(
            test_folder_exists(vault_path / folder)
        )
    print()
    
    # Test Documentation
    print("📚 Documentation:")
    doc_files = [
        'GOLD_TIER_README.md',
        'SILVER_TIER_README.md',
        'SILVER_TIER_COMPLETE.md',
    ]
    
    for filename in doc_files:
        results['Documentation'].append(
            test_file_exists(vault_path / filename)
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
    
    overall_percentage = (passed / total * 100) if total > 0 else 0
    print()
    print(f"Overall: {passed}/{total} ({overall_percentage:.0f}%)")
    
    if overall_percentage >= 90:
        print("\n✅ Gold Tier installation complete!")
        print("\nNext steps:")
        print("1. Configure .env with your API credentials")
        print("2. Setup MCP servers in Claude Code config")
        print("3. Install Odoo Community (optional for ERP features)")
        print("4. Run: python orchestrator.py")
    elif overall_percentage >= 70:
        print("\n⚠️  Most components installed. Check missing items above.")
    else:
        print("\n❌ Several components missing. Review test results.")


if __name__ == '__main__':
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path(__file__).parent
    
    run_tests(vault_path)
