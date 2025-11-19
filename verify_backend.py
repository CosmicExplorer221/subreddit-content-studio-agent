#!/usr/bin/env python3
"""
Quick startup script to verify backend is working
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def main():
    print("=" * 50)
    print("LinkedIn Automation - Backend Verification")
    print("=" * 50)
    print()

    # Check Python version
    print(f"✓ Python version: {sys.version.split()[0]}")

    # Check if data directory exists
    data_dir = os.path.join('backend', 'data')
    if os.path.exists(data_dir):
        print(f"✓ Data directory exists: {data_dir}")

        # Check subdirectories
        subdirs = ['categories', 'templates', 'posts', 'settings']
        for subdir in subdirs:
            path = os.path.join(data_dir, subdir)
            if os.path.exists(path):
                count = len([f for f in os.listdir(path) if f.endswith('.json')])
                print(f"  - {subdir}: {count} files")
    else:
        print(f"⚠ Data directory missing: {data_dir}")
        print("  Run: python -m backend.app.core.initialize")

    print()

    # Try to import main app
    try:
        from app.main import app
        print("✓ FastAPI app imports successfully")
    except Exception as e:
        print(f"✗ Failed to import app: {e}")
        print("\nTo fix:")
        print("1. cd backend")
        print("2. pip install -r requirements.txt")
        return 1

    print()
    print("Backend is ready!")
    print()
    print("To start the backend:")
    print("  cd backend")
    print("  python -m app.main")
    print()
    print("Or use the launcher scripts:")
    print("  Windows: start.bat")
    print("  Unix/Mac: ./start.sh")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
