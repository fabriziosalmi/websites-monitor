#!/usr/bin/env python3
"""
Debug version of the scheduler to identify issues
"""

import time
import subprocess
import os
import sys
from datetime import datetime

print("=== Debug Scheduler Starting ===")
print(f"Python version: {sys.version}")
print(f"Working directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")
print(f"Logs directory exists: {os.path.exists('/app/logs')}")

# Test creating logs directory
try:
    os.makedirs('/app/logs', exist_ok=True)
    print("✓ Logs directory created/exists")
except Exception as e:
    print(f"✗ Error creating logs directory: {e}")

# Test if main.py exists and is readable
if os.path.exists('main.py'):
    print("✓ main.py exists")
    try:
        with open('main.py', 'r') as f:
            content = f.read()
        print(f"✓ main.py is readable ({len(content)} characters)")
    except Exception as e:
        print(f"✗ Error reading main.py: {e}")
else:
    print("✗ main.py does not exist")

print("=== Testing subprocess call ===")
try:
    result = subprocess.run(
        ['python', '--version'], 
        capture_output=True, 
        text=True,
        timeout=10
    )
    print(f"✓ Subprocess test successful: {result.stdout.strip()}")
except Exception as e:
    print(f"✗ Subprocess test failed: {e}")

print("=== Testing main.py execution ===")
try:
    # Try to run main.py with a short timeout
    result = subprocess.run(
        ['python', 'main.py', '--help'], 
        capture_output=True, 
        text=True,
        timeout=5
    )
    print(f"✓ main.py --help exit code: {result.returncode}")
    if result.stdout:
        print(f"stdout: {result.stdout[:200]}...")
    if result.stderr:
        print(f"stderr: {result.stderr[:200]}...")
except subprocess.TimeoutExpired:
    print("⚠ main.py --help timed out")
except Exception as e:
    print(f"✗ Error running main.py --help: {e}")

print("=== Debug complete ===")
