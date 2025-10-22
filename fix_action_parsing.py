# This fixes the parse_action_statement method to parse directly instead of calling parse_action_literal

def fixed_parse_action_statement(self):
    print("🔧 FIXED parse_action_statement called")
    
    # We're at the ACTION token, need to parse: action name ( params ) { body }
    
    # Skip the 'action' token and get the function name
    if not self.expect_peek(IDENT):
        print("❌ Expected function name after 'action'")
        return None
        
    func_name = Identifier(value=self.cur_token.literal)
    print(f"🔧 Function name: {func_name.value}")
    
    # Expect '(' after function name
    if not self.expect_peek(LPAREN):
        print("❌ Expected '(' after function name")
        return None
        
    # Parse parameters (skip the '(' )
    self.next_token()  # Now at '('
    parameters = self.parse_action_parameters()
    print(f"🔧 Parameters: {[p.value for p in parameters]}")
    
    # Expect '{' after parameters  
    if not self.expect_peek(LBRACE):
        print("❌ Expected '{' after parameters")
        return None
        
    # Parse function body
    body = self.parse_block_statement()
    print(f"🔧 Body has {len(body.statements)} statements")
    
    # Create the function as: let function_name = action(params) {body}
    action_literal = ActionLiteral(parameters=parameters, body=body)
    let_stmt = LetStatement(name=func_name, value=action_literal)
    
    print("🔧 Successfully created function definition")
    return let_stmt

# Now let's test this fixed approach
from lexer import Lexer
from parser import Parser

# Replace the broken method
Parser.parse_action_statement = fixed_parse_action_statement

source = '''action simplest():
    return "function_works"'''

print("=== TESTING FIXED PARSER ===")
lexer = Lexer(source)
parser = Parser(lexer)

program = parser.parse_program()

print(f"Parser errors: {parser.errors}")
print(f"Number of statements: {len(program.statements)}")

for i, stmt in enumerate(program.statements):
    print(f"Statement {i}: {type(stmt).__name__}")
    if hasattr(stmt, 'name'):
        print(f"  Name: {stmt.name.value}")
    if hasattr(stmt, 'value'):
        val = stmt.value
        print(f"  Value type: {type(val).__name__}")
        if hasattr(val, 'parameters'):
            print(f"    Parameters: {[p.value for p in val.parameters]}")
        if hasattr(val, 'body'):
            print(f"    Body statements: {len(val.body.statements)}")
