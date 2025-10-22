#!/usr/bin/env python3
from lexer import Lexer

source_code = '''action simplest():
    return "function_works"'''

print("=== TOKEN DEBUG ===")
lexer = Lexer(source_code)

while True:
    token = lexer.next_token()
    print(f"Token: {token.type} -> '{token.literal}'")
    if token.type == 'EOF':
        break
