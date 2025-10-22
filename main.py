
#!/usr/bin/env python3
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer
from parser import Parser
from evaluator import eval_node
from object import Environment

def main():
    if len(sys.argv) != 2:
        print("Usage: zx <filename.zx>")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
        sys.exit(1)
    
    # Create lexer and parser
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    program = parser.parse_program()
    
    if len(parser.errors) > 0:
        for error in parser.errors:
            print(f"PARSER ERROR: {error}")
        sys.exit(1)
    
    # Evaluate the program
    env = Environment()
    result = eval_node(program, env)
    
    # Print result if it's not null
    if result and hasattr(result, 'inspect') and result.inspect() != 'null':
        print(result.inspect())

if __name__ == "__main__":
    main()
