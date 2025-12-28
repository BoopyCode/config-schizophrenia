#!/usr/bin/env python3
"""Config Schizophrenia - Because your configs have multiple personalities"""

import os
import sys
import json
import difflib
from pathlib import Path
from collections import defaultdict

# The voices in your config's head
ENVIRONMENTS = ['local', 'staging', 'production']
CONFIG_PATTERNS = ['.env', 'config*.json', 'settings*.py', '*.yaml', '*.yml']

def find_config_files():
    """Hunt down those sneaky configs hiding in plain sight"""
    configs = defaultdict(list)
    for pattern in CONFIG_PATTERNS:
        for path in Path('.').rglob(pattern):
            # Skip virtual environments and build directories
            if any(part in str(path) for part in ['__pycache__', 'venv', '.git', 'node_modules']):
                continue
            configs[path.name].append(str(path))
    return configs

def compare_configs(configs):
    """Let's see who's not playing nice with the others"""
    issues = []
    for filename, paths in configs.items():
        if len(paths) > 1:
            # Read all versions of this config
            contents = []
            for path in paths:
                try:
                    with open(path, 'r') as f:
                        contents.append((path, f.read()))
                except Exception as e:
                    contents.append((path, f"ERROR: {e}"))
            
            # Check if they're identical (they never are)
            if len(set(content for _, content in contents)) > 1:
                issues.append({
                    'file': filename,
                    'paths': paths,
                    'differences': True
                })
    return issues

def check_env_vars():
    """Environment variables: the ghosts in the machine"""
    # Just check for some common troublemakers
    suspects = ['DATABASE_URL', 'API_KEY', 'SECRET', 'DEBUG', 'ENVIRONMENT']
    missing = []
    for suspect in suspects:
        if suspect in os.environ:
            value = os.environ[suspect]
            # Don't show actual secrets, just hint at problems
            if 'localhost' in str(value) and 'production' in os.environ.get('ENVIRONMENT', ''):
                missing.append(f"{suspect}: Using localhost in production? Bold.")
        else:
            missing.append(f"{suspect}: Not set (probably fine... probably)")
    return missing

def main():
    """The intervention"""
    print("\n🔍 Config Schizophrenia Diagnosis\n")
    
    # Phase 1: Multiple personality configs
    print("1. Multiple Config Personalities:")
    configs = find_config_files()
    issues = compare_configs(configs)
    
    if issues:
        for issue in issues:
            print(f"   • {issue['file']} has {len(issue['paths'])} different versions")
            for path in issue['paths']:
                print(f"     - {path}")
    else:
        print("   ✓ All configs are consistent (unlikely)")
    
    # Phase 2: Environment variable ghosts
    print("\n2. Environment Variable Ghosts:")
    env_issues = check_env_vars()
    if env_issues:
        for issue in env_issues:
            print(f"   • {issue}")
    else:
        print("   ✓ No obvious env var issues (check again)")
    
    # Diagnosis
    print("\n📋 Diagnosis:")
    if issues or env_issues:
        print("   Your configs have multiple personalities.")
        print("   Prescription: Pick one identity and stick with it.")
        return 1
    else:
        print("   Configs appear stable (for now).")
        print("   Warning: This tool has 99% accuracy. You're probably the 1%.")
        return 0

if __name__ == '__main__':
    sys.exit(main())
