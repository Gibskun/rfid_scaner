#!/usr/bin/env python3
"""
RFID Project Cleanup Script
Removes test files, documentation, and unused files that don't affect main.py execution
"""

import os
import shutil
from pathlib import Path

def cleanup_project():
    """Clean up the RFID project directory"""
    
    # CORE FILES REQUIRED BY main.py (DO NOT DELETE)
    core_files = {
        'main.py',           # Entry point
        'transport.py',      # Serial transport
        'reader.py',         # RFID reader interface
        'response.py',       # Response handling
        'command.py',        # Command construction
        'database.py',       # Database operations
        'shared_data.py',    # Shared data between scanner and web
        'web_interface.py',  # Web interface
        'requirements.txt',  # Dependencies
    }
    
    # TEMPLATE FILES (REQUIRED BY WEB INTERFACE)
    template_files = {
        'templates/dashboard.html',
        'templates/main_dashboard.html', 
        'templates/deactivate_dashboard.html',
        'templates/delete_dashboard.html',
        'templates/status_dashboard.html'
    }
    
    # FILES TO DELETE - Test files, documentation, duplicates, utilities
    files_to_delete = [
        # Test files (all test_*.py files)
        'test_auto_deactivate_mode.py',
        'test_auto_unregister.py', 
        'test_compatibility.py',
        'test_custom_id_system.py',
        'test_database.py',
        'test_deactivate_functionality.py',
        'test_epc_generation.py',
        'test_historical_data.py',
        'test_import.py',
        'test_shared_data.py',
        'test_status_workflow.py',
        'test_tag_simulator.py',
        'test_web_only.py',
        
        # Documentation files (all *.md files)
        'ALL_IN_ONE_SUCCESS.md',
        'AUTO_DEACTIVATE_SUCCESS.md',
        'AUTO_UNREGISTRATION_SUMMARY.md',
        'BEFORE_AFTER_COMPARISON.md',
        'COMPLETE_FEATURES.md',
        'DEACTIVATION_SYSTEM_SUMMARY.md',
        'FIX_SUMMARY.md',
        'INTERACTIVE_MODE_GUIDE.md',
        'MAIN_INTERACTIVE_COMPLETE.md',
        'NEW_WORKFLOW_GUIDE.md',
        'QUICK_REFERENCE.md',
        'QUICK_START.md',
        'QUICK_START_DATABASE.md',
        'README_AUTO_START.md',
        'README_DATABASE.md',
        'SINGLE_TERMINAL_SUCCESS.md',
        'SYSTEM_FIXED.md',
        'UPDATE_SUMMARY.md',
        'WEB_INTERFACE_SUMMARY.md',
        
        # Utility/launcher files (not needed for main.py)
        'auto_launch.py',
        'launch_web.py',
        'rfid_web_auto.py',
        'interactive_scanner.py',
        'clear_database.py',
        'check_database_status.py',
        'check_tags.py',
        
        # Old/duplicate files
        'web_interface_old.py',
        
        # Batch files
        '1_CLEAR_DATABASE.bat',
        '2_INTERACTIVE_SCANNER.bat',
        
        # PowerShell scripts
        'check_installation.ps1',
    ]
    
    # DIRECTORIES TO DELETE
    directories_to_delete = [
        'archive',    # Contains old/experimental code
        'image',      # Screenshots/images not needed for runtime
        '__pycache__', # Python cache (will be regenerated)
    ]
    
    print("🧹 RFID PROJECT CLEANUP")
    print("=" * 60)
    print("This will remove test files, documentation, and unused utilities")
    print("CORE SYSTEM FILES WILL BE PRESERVED:")
    print()
    for file in sorted(core_files):
        print(f"  ✅ {file}")
    print()
    for template in sorted(template_files):
        print(f"  ✅ {template}")
    print()
    
    # Show what will be deleted
    current_dir = Path('.')
    
    print("FILES TO BE DELETED:")
    deleted_count = 0
    for file_path in files_to_delete:
        if (current_dir / file_path).exists():
            print(f"  🗑️  {file_path}")
            deleted_count += 1
        else:
            print(f"  ⚠️  {file_path} (not found)")
    
    print(f"\\nDIRECTORIES TO BE DELETED:")
    for dir_path in directories_to_delete:
        if (current_dir / dir_path).exists():
            print(f"  🗂️  {dir_path}/")
            deleted_count += 1
        else:
            print(f"  ⚠️  {dir_path}/ (not found)")
    
    print(f"\\n📊 SUMMARY:")
    print(f"  Core files preserved: {len(core_files) + len(template_files)}")
    print(f"  Files/folders to delete: {deleted_count}")
    print()
    
    # Confirm deletion
    response = input("Continue with cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Cleanup cancelled")
        return False
    
    print("\\n🗑️  Starting cleanup...")
    
    # Delete files
    deleted_files = 0
    for file_path in files_to_delete:
        full_path = current_dir / file_path
        if full_path.exists():
            try:
                full_path.unlink()
                print(f"  ✅ Deleted: {file_path}")
                deleted_files += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {file_path}: {e}")
    
    # Delete directories
    deleted_dirs = 0
    for dir_path in directories_to_delete:
        full_path = current_dir / dir_path
        if full_path.exists():
            try:
                shutil.rmtree(full_path)
                print(f"  ✅ Deleted directory: {dir_path}/")
                deleted_dirs += 1
            except Exception as e:
                print(f"  ❌ Failed to delete {dir_path}/: {e}")
    
    print(f"\\n🎉 CLEANUP COMPLETE!")
    print(f"  Files deleted: {deleted_files}")
    print(f"  Directories deleted: {deleted_dirs}")
    print()
    print("🚀 Your project is now clean and ready!")
    print("✅ Run 'python main.py' to start the system")
    
    return True

def verify_core_system():
    """Verify that core system files still exist after cleanup"""
    print("\\n🔍 VERIFYING CORE SYSTEM FILES...")
    
    core_files = [
        'main.py',
        'transport.py', 
        'reader.py',
        'response.py',
        'command.py',
        'database.py',
        'shared_data.py',
        'web_interface.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in core_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"  ❌ MISSING: {file}")
        else:
            print(f"  ✅ OK: {file}")
    
    # Check templates
    template_dir = Path('templates')
    if template_dir.exists():
        template_files = list(template_dir.glob('*.html'))
        print(f"  ✅ Templates directory: {len(template_files)} HTML files")
    else:
        print(f"  ❌ MISSING: templates/ directory")
        missing_files.append('templates/')
    
    if missing_files:
        print(f"\\n⚠️  WARNING: {len(missing_files)} core files are missing!")
        print("The system may not work properly.")
        return False
    else:
        print("\\n✅ All core files verified - system should work properly!")
        return True

if __name__ == "__main__":
    try:
        cleanup_project()
        verify_core_system()
    except KeyboardInterrupt:
        print("\\n❌ Cleanup cancelled by user")
    except Exception as e:
        print(f"\\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()