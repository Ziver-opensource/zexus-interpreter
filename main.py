# ~/zexus-interpreter/main.py (UPDATED)
#!/usr/bin/env python3
"""
Legacy runner - now uses the new CLI system with syntax validation
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from zexus.cli.main import cli

if __name__ == "__main__":
    # If no arguments, show help
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    # Support legacy: zx filename.zx → zx run filename.zx  
    if len(sys.argv) == 2 and sys.argv[1].endswith('.zx'):
        sys.argv.insert(1, 'run')

    # Support syntax style flag in legacy mode
    if len(sys.argv) >= 3 and any('--syntax-style' in arg for arg in sys.argv):
        # Already has syntax style flag, just run
        pass
    else:
        # Add default syntax style
        sys.argv.append('--syntax-style=auto')

    # Enable advanced parsing by default
    if not any('--no-advanced-parsing' in arg for arg in sys.argv):
        sys.argv.append('--advanced-parsing')

    cli()