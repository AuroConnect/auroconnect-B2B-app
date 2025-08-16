#!/usr/bin/env python3
"""
Cleanup Unwanted Files Script
Removes temporary and test files that are no longer needed
"""

import os
import shutil
import glob

def cleanup_unwanted_files():
    """Remove unwanted files and directories"""
    
    # List of files to remove
    files_to_remove = [
        # Test and debug files
        'test_*.py',
        'debug_*.py',
        'fix_*.py',
        'check_*.py',
        'clear_*.py',
        'reset_*.py',
        'update_*.py',
        'quick_test.py',
        'test_api.py',
        'test_login.py',
        'test_registration.py',
        'test_system_status.py',
        'test_server_connection.py',
        'test_frontend_api.py',
        'test_frontend_with_ec2.py',
        'test_partnership_flow.py',
        'test_partnership_system.py',
        'test_ec2_partnership_flow.py',
        'test_email_functionality.py',
        'test_localhost_setup.py',
        'test_complete_flow.py',
        'test_cache_fix.py',
        'test_api_fix.py',
        'debug_api.py',
        'debug_invitation.py',
        'fix_blank_screen.py',
        'fix_frontend_blank_screen.py',
        'fix_frontend_issues.py',
        'fix_common_issues.py',
        'fix_database.py',
        'fix_and_test.py',
        'fix_and_test_complete.py',
        'clear_and_test.py',
        'check_database_schema.py',
        'check_partnership_data.py',
        'check_partnerships.py',
        'check_user_ids.py',
        'reset_and_seed_2x2.py',
        'reset_and_test_partnership.py',
        'restart_containers.py',
        'setup_complete_2x2_system.py',
        'update_test_accounts.py',
        'update_user_emails.py',
        'execute_sql.py',
        'add_message_column.sql',
        
        # HTML test files
        'test_frontend.html',
        'test_invitation_page.html',
        'debug_frontend.html',
        'emergency_fix.html',
        'force_refresh.html',
        'test_routing.html',
        
        # JavaScript files
        'clear_cache.js',
        
        # Documentation files (keep only essential ones)
        'CLEAN_REPOSITORY_SUMMARY.md',
        'EC2_PARTNERSHIP_SUCCESS.md',
        'EMAIL_SETUP_GUIDE.md',
        'FRONTEND_FIX_GUIDE.md',
        'LOCALHOST_SETUP.md',
        'MANUAL_TEST_GUIDE.md',
        'FINAL_STATUS.md',
        
        # Backup directories
        'backups/',
        'logs/',
        'uploads/',
        'instance/',
        'ssl/',
        
        # Python cache files
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        
        # Node modules (will be reinstalled)
        'client/node_modules/',
        'client/dist/',
        'client/.vite/',
        
        # Environment files (keep example)
        '.env',
        
        # Docker volumes (will be recreated)
        'server/instance/',
        'instance/'
    ]
    
    print("🧹 Cleaning up unwanted files...")
    print("=" * 50)
    
    removed_count = 0
    error_count = 0
    
    for pattern in files_to_remove:
        try:
            # Handle glob patterns
            if '*' in pattern or '?' in pattern:
                matches = glob.glob(pattern, recursive=True)
                for match in matches:
                    if os.path.exists(match):
                        if os.path.isdir(match):
                            shutil.rmtree(match)
                            print(f"🗑️  Removed directory: {match}")
                        else:
                            os.remove(match)
                            print(f"🗑️  Removed file: {match}")
                        removed_count += 1
            else:
                # Handle specific files/directories
                if os.path.exists(pattern):
                    if os.path.isdir(pattern):
                        shutil.rmtree(pattern)
                        print(f"🗑️  Removed directory: {pattern}")
                    else:
                        os.remove(pattern)
                        print(f"🗑️  Removed file: {pattern}")
                    removed_count += 1
                    
        except Exception as e:
            print(f"❌ Error removing {pattern}: {e}")
            error_count += 1
    
    # Clean up Python cache directories recursively
    print("\n🧹 Cleaning Python cache directories...")
    for root, dirs, files in os.walk('.'):
        if '__pycache__' in dirs:
            cache_dir = os.path.join(root, '__pycache__')
            try:
                shutil.rmtree(cache_dir)
                print(f"🗑️  Removed cache: {cache_dir}")
                removed_count += 1
            except Exception as e:
                print(f"❌ Error removing cache {cache_dir}: {e}")
                error_count += 1
    
    # Clean up .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.pyc', '.pyo', '.pyd')):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"🗑️  Removed cache file: {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"❌ Error removing cache file {file_path}: {e}")
                    error_count += 1
    
    print(f"\n✅ Cleanup completed!")
    print(f"   📊 Files/Directories removed: {removed_count}")
    print(f"   ❌ Errors encountered: {error_count}")
    
    # Show remaining files
    print(f"\n📁 Remaining files in project:")
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        level = root.replace('.', '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:  # Show first 10 files
            print(f"{subindent}{file}")
        if len(files) > 10:
            print(f"{subindent}... and {len(files) - 10} more files")

def main():
    """Main function"""
    print("🧹 Project Cleanup Script")
    print("=" * 50)
    
    # Confirm before proceeding
    response = input("Are you sure you want to remove unwanted files? (y/N): ")
    if response.lower() != 'y':
        print("❌ Cleanup cancelled")
        return
    
    cleanup_unwanted_files()
    
    print("\n🎉 Project cleanup completed!")
    print("\n📋 Summary:")
    print("   ✅ Removed test and debug files")
    print("   ✅ Removed temporary HTML files")
    print("   ✅ Removed Python cache files")
    print("   ✅ Removed backup directories")
    print("   ✅ Kept essential project files")
    print("\n🚀 Project is now clean and ready!")

if __name__ == "__main__":
    main()
