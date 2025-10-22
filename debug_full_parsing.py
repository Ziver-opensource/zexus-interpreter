#!/usr/bin/env python3
import sys
from lexer import Lexer
from parser import Parser
from zexus_token import *

def debug_full_parsing(source_code):
    print("=== FULL PARSING DEBUG ===")
    print("Source code:")
    print(repr(source_code))
    print()
    
    # Tokenize
    print("=== TOKEN STREAM ===")
    lexer = Lexer(source_code)
    token = lexer.next_token()
    tokens = []
    while token.type != EOF:
        tokens.append(token)
        print(f"Token: {token.type:10} -> '{token.literal}'")
        token = lexer.next_token()
    tokens.append(token)
    print(f"Token: {token.type:10} -> '{token.literal}'")
    print()
    
    # Parse
    print("=== PARSING ===")
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    
    # Check initial tokens
    print(f"Initial cur_token:  {parser.cur_token.type:10} -> '{parser.cur_token.literal}'")
    print(f"Initial peek_token: {parser.peek_token.type:10} -> '{parser.peek_token.literal}'")
    print()
    
    program = parser.parse_program()
    
    print(f"Parser errors: {parser.errors}")
    print(f"Number of statements: {len(program.statements)}")
    print()
    
    for i, stmt in enumerate(program.statements):
        print(f"Statement {i}: {type(stmt).__name__}")
        if hasattr(stmt, 'name'):
            print(f"  Name: {stmt.name.value if hasattr(stmt.name, 'value') else stmt.name}")
        if hasattr(stmt, 'value'):
            val = stmt.value
            print(f"  Value: {type(val).__name__}")
            if hasattr(val, 'function'):
                print(f"    Function: {val.function}")
            if hasattr(val, 'parameters'):
                print(f"    Parameters: {[p.value for p in val.parameters]}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    else:
        source = '''action simplest():
    return "function_works"'''
    
    debug_full_parsing(source)
