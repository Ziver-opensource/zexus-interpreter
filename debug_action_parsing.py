from lexer import Lexer
from parser import Parser

# Monkey-patch the parser to add debug output
original_parse_action_literal = Parser.parse_action_literal
original_parse_action_statement = Parser.parse_action_statement

def debug_parse_action_literal(self):
    print("🔍 parse_action_literal CALLED")
    print(f"   Current token: {self.cur_token.type} -> '{self.cur_token.literal}'")
    print(f"   Peek token: {self.peek_token.type} -> '{self.peek_token.literal}'")
    
    result = original_parse_action_literal(self)
    print(f"🔍 parse_action_literal RETURNED: {result}")
    return result

def debug_parse_action_statement(self):
    print("🎯 parse_action_statement CALLED")
    result = original_parse_action_statement(self)
    print(f"🎯 parse_action_statement RETURNED: {result}")
    return result

Parser.parse_action_literal = debug_parse_action_literal
Parser.parse_action_statement = debug_parse_action_statement

# Now test it
source = '''action simplest():
    return "function_works"'''

print("=== DEBUGGING ACTION PARSING ===")
lexer = Lexer(source)
parser = Parser(lexer)

print(f"Initial token: {parser.cur_token.type} -> '{parser.cur_token.literal}'")
print(f"Peek token: {parser.peek_token.type} -> '{parser.peek_token.literal}'")

program = parser.parse_program()

print(f"Parser errors: {parser.errors}")
print(f"Number of statements: {len(program.statements)}")
