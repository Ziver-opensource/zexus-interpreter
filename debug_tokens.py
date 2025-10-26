# debug_tokens.py
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from zexus_token import *

def debug_tokens(filename):
    with open(filename, 'r') as f:
        source_code = f.read()
    
    lexer = Lexer(source_code)
    
    print("=== TOKEN DEBUG ===")
    token_count = 0
    while True:
        token = lexer.next_token()
        print(f"Token {token_count}: {token.type} -> '{token.literal}'")
        token_count += 1
        
        if token.type == EOF:
            break
        if token_count > 100:  # Safety limit
            print("Too many tokens, stopping...")
            break

if __name__ == "__main__":
    debug_tokens("test_multi_language_fixed.zx")