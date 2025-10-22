#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser

def debug_parse(filename):
    with open(filename, 'r') as f:
        source_code = f.read()
    
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    print("=== PARSER DEBUG ===")
    print(f"Source: {filename}")
    print(f"Parser errors: {parser.errors}")
    print(f"Number of statements: {len(program.statements)}")
    
    for i, stmt in enumerate(program.statements):
        print(f"Statement {i}: {type(stmt).__name__}")
        if hasattr(stmt, 'expression'):
            print(f"  Expression: {type(stmt.expression).__name__}")
    
    return program

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_parser.py <filename.zx>")
        sys.exit(1)
    
    debug_parse(sys.argv[1])
