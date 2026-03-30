"""
Test Script - Silver Tier Verification
Part of Personal AI Employee Silver Tier

Run this script to verify all components are working correctly.

Usage:
    python test_silver_tier.py
"""

import sys
import subprocess
from pathlib import Path


def test_import(module_name: str, install_name: str = None) -> bool:
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
        return True
    except ImportError as e:
        print(f"✗ {module_name} - {e}")
        if install_name:
            print(f"  Install: pip install {install_name}")
        return False


def test_file_exists(filepath: Path) -> bool:
    """Test if a file exists"""
    if filepath.exists():
        print(f"✓ {filepath.name}")
        return True
    else:
        print(f"✗ {filepath.name} - Not found")
        return False


def run_tests(vault_path: Path):
    """Run all tests"""
    print("=" * 60)
    print("Personal AI Employee - Silver Tier Tests")
    print("=" * 60)
    print()
    
    results = {
        'Python Dependencies': [],
        'Source Files': [],
        'Folders': [],
        'Config Files': [],
    }
    
    # Test Python dependencies
    print("📦 Python Dependencies:")
    deps = [
        ('watchdog', 'watchdog'),
        ('dotenv', 'python-dotenv'),
        ('googleapiclient', 'google-api-python-client'),
        ('google_auth_oauthlib', 'google-auth-oauthlib'),
        ('playwright', 'playwright'),
        ('requests', 'requests'),
        ('pydantic', 'pydantic'),
    ]
    
    for module, install_name in deps:
        results['Python Dependencies'].append(test_import(module, install_name))
    
    print()
    
    # Test source files
    print("📄 Source Files:")
    src_files = [
        'base_watcher.py',
        'gmail_watcher.py',
        'whatsapp_watcher.py',
        'linkedin_poster.py',
        'plan_generator.py',
        'approval_manager.py',
        'orchestrator.py',
    ]
    
    for filename in src_files:
        results['Source Files'].append(test_file_exists(vault_path / 'src' / filename))
    
    print()
    
    # Test folders
    print("📁 Folders:")
    folders = [
        'Inbox',
        'Needs_Action',
        'Plans',
        'Pending_Approval',
        'Approved',
        'Rejected',
        'Done',
        'Briefings',
        'Logs',
        'Accounting',
        'Invoices',
    ]
    
    for folder in folders:
        folder_path = vault_path / folder
        if folder_path.exists() and folder_path.is_dir():
            print(f"✓ {folder}/")
            results['Folders'].append(True)
        else:
            print(f"✗ {folder}/ - Not found")
            results['Folders'].append(False)
    
    print()
    
    # Test config files
    print("⚙️  Config Files:")
    config_files = [
        '.env.example',
        'Dashboard.md',
        'Business_Goals.md',
        'Company_Handbook.md',
        'SILVER_TIER_README.md',
    ]
    
    for filename in config_files:
        results['Config Files'].append(test_file_exists(vault_path / filename))
    
    print()
    
    # Test MCP server
    print("🔌 MCP Server:")
    mcp_files = [
        vault_path / 'src' / 'mcp-linkedin' / 'package.json',
        vault_path / 'src' / 'mcp-linkedin' / 'index.js',
        vault_path / 'src' / 'mcp-linkedin' / '.env.example',
    ]
    
    for filepath in mcp_files:
        test_file_exists(filepath)
    
    print()
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
            print(f"{category}: {category_passed}/{category_total} ({percentage:.0f}%)")
    
    overall_percentage = (passed / total * 100) if total > 0 else 0
    print()
    print(f"Overall: {passed}/{total} ({overall_percentage:.0f}%)")
    
    if overall_percentage >= 90:
        print("\n✅ All critical components installed!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and fill in your credentials")
        print("2. For Gmail: Setup Google Cloud credentials")
        print("3. For LinkedIn: Run 'python linkedin_poster.py --login'")
        print("4. Run orchestrator: 'python orchestrator.py'")
    else:
        print("\n⚠️  Some components are missing. Check the errors above.")
        print("Install missing dependencies with:")
        print("  pip install -r src/requirements.txt")


if __name__ == '__main__':
    # Get vault path
    if len(sys.argv) > 1:
        vault_path = Path(sys.argv[1])
    else:
        vault_path = Path(__file__).parent
    
    run_tests(vault_path)
