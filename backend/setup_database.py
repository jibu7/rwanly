#!/usr/bin/env python3
"""
Master Database Setup Script
This script provides a convenient way to clean and reload business data.
"""

import os
import sys
import subprocess
from pathlib import Path


def run_script(script_name, description):
    """Run a Python script and return success status."""
    print(f"\n🔄 {description}...")
    script_path = Path(__file__).parent / script_name
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                               capture_output=True, text=True, input="YES\n")
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running {script_name}: {str(e)}")
        return False


def main():
    """Main menu for database operations."""
    print("=" * 80)
    print("🗄️  DATABASE MANAGEMENT SYSTEM")
    print("=" * 80)
    print()
    print("Available operations:")
    print("1. Clean database only")
    print("2. Load business data only")
    print("3. Clean and reload all data (recommended)")
    print("4. Exit")
    print()
    
    while True:
        try:
            choice = input("Select operation (1-4): ").strip()
            
            if choice == "1":
                # Clean only
                print("\n🧹 Cleaning database...")
                if run_script("cleanup_database.py", "Database cleanup"):
                    print("\n✅ Database cleaned successfully!")
                else:
                    print("\n❌ Database cleanup failed!")
                break
                
            elif choice == "2":
                # Load data only
                print("\n📊 Loading business data...")
                if run_script("load_business_data.py", "Business data loading"):
                    print("\n✅ Business data loaded successfully!")
                else:
                    print("\n❌ Business data loading failed!")
                break
                
            elif choice == "3":
                # Clean and reload
                print("\n🔄 Performing complete database reset...")
                
                # First clean
                if not run_script("cleanup_database.py", "Database cleanup"):
                    print("\n❌ Setup failed at cleanup stage!")
                    break
                
                # Then load data
                if not run_script("load_business_data.py", "Business data loading"):
                    print("\n❌ Setup failed at data loading stage!")
                    break
                
                print("\n" + "=" * 80)
                print("🎉 COMPLETE DATABASE SETUP SUCCESSFUL!")
                print("=" * 80)
                print("Your ERP system is ready with fresh business data!")
                print()
                print("Next steps:")
                print("  1. Start the backend server: ./dev.sh")
                print("  2. Start the frontend: cd ../frontend && npm run dev")
                print("  3. Access the system at http://localhost:3000")
                print("  4. Login with username: admin")
                print("=" * 80)
                break
                
            elif choice == "4":
                print("👋 Goodbye!")
                return 0
                
            else:
                print("❌ Invalid choice. Please select 1-4.")
                continue
                
        except KeyboardInterrupt:
            print("\n\n👋 Operation cancelled by user.")
            return 1
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
