#!/usr/bin/env python3
import sys
from lexer import Lexer
from parser import Parser

def debug_parser_detailed(source_code):
    print("=== DETAILED PARSER DEBUG ===")
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print(f"Parser errors: {parser.errors}")
    print(f"Number of statements: {len(program.statements)}")
    
    for i, stmt in enumerate(program.statements):
        print(f"Statement {i}: {type(stmt).__name__}")
        if hasattr(stmt, 'name'):
            print(f"  Name: {stmt.name}")
        if hasattr(stmt, 'value'):
            print(f"  Value type: {type(stmt.value).__name__}")
        if hasattr(stmt, 'expression'):
            print(f"  Expression type: {type(stmt.expression).__name__}")
        if hasattr(stmt, 'body'):
            print(f"  Body statements: {len(stmt.body.statements) if stmt.body else 0}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
    else:
        source = '''action simplest():
    return "function_works"'''
    
    debug_parser_detailed(source)
