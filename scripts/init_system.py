#!/usr/bin/env python
"""
System initialization script
Sets up database, creates directories, and builds initial product universe
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/cache',
        'data/temp',
        'data/downloads',
        'logs',
        'reports',
        'exports'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Created directory structure")


def initialize_database():
    """Initialize database schema"""
    try:
        from database.session import init_db
        init_db()
        print("✓ Database schema created")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main initialization function"""
    print("\n" + "="*50)
    print("SA Investment Analyzer - System Initialization")
    print("="*50 + "\n")
    
    # Setup
    print("Setting up system...\n")
    create_directories()
    initialize_database()
    
    # Show completion message
    print("\n" + "="*50)
    print("✅ Setup Complete!")
    print("="*50)
    print("\nNext steps:")
    print("  1. Edit .env file with your settings")
    print("  2. Run: streamlit run app.py")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInitialization cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)