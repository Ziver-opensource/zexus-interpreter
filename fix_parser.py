# Let's patch the parser to properly handle ACTION tokens
import sys
import os

# Read the current parser
with open('parser.py', 'r') as f:
    parser_content = f.read()

# Check if parse_statement handles ACTION correctly
if "elif self.cur_token_is(ACTION):" in parser_content and "return self.parse_action_statement()" in parser_content:
    print("✅ Parser already has ACTION handling in parse_statement")
else:
    print("❌ Parser is MISSING ACTION handling in parse_statement!")
    
# Let's see the exact current parse_statement method
lines = parser_content.split('\n')
in_parse_statement = False
for i, line in enumerate(lines):
    if "def parse_statement(self):" in line:
        in_parse_statement = True
        print(f"\n=== CURRENT parse_statement method (lines {i+1}-{i+20}): ===")
    if in_parse_statement and i > 0:
        print(f"{i+1}: {line}")
        if "def " in line and "parse_statement" not in line:
            break

# Let's also check if parse_action_statement exists
if "def parse_action_statement(self):" in parser_content:
    print("\n✅ parse_action_statement method exists")
else:
    print("\n❌ parse_action_statement method is MISSING!")
