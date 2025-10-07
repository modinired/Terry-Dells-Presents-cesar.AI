#!/usr/bin/env python3
"""
Test file with obvious issues for background agents to detect.
"""

# TODO: This is a test file
# FIXME: Remove this file after testing

import os
import sys

# Hardcoded values
API_KEY = "sk-1234567890abcdef"
PASSWORD = "secretpassword123"

def bad_function():
    # Missing docstring
    print("This function has no docstring")
    eval("print('dangerous eval')")
    exec("print('dangerous exec')")
    
    # Hardcoded localhost
    url = "http://localhost:8000/api"
    
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    return "done"

def another_bad_function():
    # Another function without docstring
    pass

# Unused import
import json  # This import is never used

# Print statement for debugging
print("Debug info")

# More hardcoded values
DATABASE_URL = "postgresql://user:pass@localhost:5432/db" 