# This script will fix the indentation in evaluator.py
import re

with open('evaluator.py', 'r') as f:
    content = f.read()

# Fix the apply_function method indentation
fixed_content = re.sub(
    r'def apply_function\(fn, args\): # UPDATED: Handles both Actions and Builtins\n  print\(f"DEBUG: Applying function {fn}, args: {args}"\)\n    """',
    r'def apply_function(fn, args): # UPDATED: Handles both Actions and Builtins\n    print(f"DEBUG: Applying function {fn}, args: {args}")\n    """',
    content
)

with open('evaluator.py', 'w') as f:
    f.write(fixed_content)

print("✅ Fixed evaluator.py indentation")
