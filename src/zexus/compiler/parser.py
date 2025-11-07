# parser.py (TOLERANT MULTI-STRATEGY PARSER)
"""
Clean Production Parser for Zexus - Fixes Object Literal Issue
"""

from ..zexus_token import *
from .lexer import Lexer
from .zexus_ast import *

# Precedence constants
LOWEST, ASSIGN_PREC, EQUALS, LESSGREATER, SUM, PRODUCT, PREFIX, CALL, LOGICAL = 1, 2, 3, 4, 5, 6, 7, 8, 9

precedences = {
    EQ: EQUALS, NOT_EQ: EQUALS,
    LT: LESSGREATER, GT: LESSGREATER, LTE: LESSGREATER, GTE: LESSGREATER,
    PLUS: SUM, MINUS: SUM,
    SLASH: PRODUCT, STAR: PRODUCT, MOD: PRODUCT,
    AND: LOGICAL, OR: LOGICAL,
    LPAREN: CALL,
    DOT: CALL,
    ASSIGN: ASSIGN_PREC,
}

class ProductionParser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.errors = []
        self.cur_token = None
        self.peek_token = None
        
        # Parser function maps
        self.prefix_parse_fns = {
            IDENT: self.parse_identifier,
            INT: self.parse_integer_literal,
            FLOAT: self.parse_float_literal,
            STRING: self.parse_string_literal,
            BANG: self.parse_prefix_expression,
            MINUS: self.parse_prefix_expression,
            TRUE: self.parse_boolean,
            FALSE: self.parse_boolean,
            LPAREN: self.parse_grouped_expression,
            IF: self.parse_if_expression,
            LBRACKET: self.parse_list_literal,
            LBRACE: self.parse_map_literal,  # FIXED: Map literal parsing
            ACTION: self.parse_action_literal,
            EMBEDDED: self.parse_embedded_literal,
            LAMBDA: self.parse_lambda_expression,
        }
        
        self.infix_parse_fns = {
            PLUS: self.parse_infix_expression,
            MINUS: self.parse_infix_expression,
            SLASH: self.parse_infix_expression,
            STAR: self.parse_infix_expression,
            MOD: self.parse_infix_expression,
            EQ: self.parse_infix_expression,
            NOT_EQ: self.parse_infix_expression,
            LT: self.parse_infix_expression,
            GT: self.parse_infix_expression,
            LTE: self.parse_infix_expression,
            GTE: self.parse_infix_expression,
            AND: self.parse_infix_expression,
            OR: self.parse_infix_expression,
            ASSIGN: self.parse_assignment_expression,
            LPAREN: self.parse_call_expression,
            DOT: self.parse_method_call_expression,
        }
        
        self.next_token()
        self.next_token()

    def parse_program(self):
        """Clean, efficient program parsing"""
        program = Program()
        while not self.cur_token_is(EOF):
            # Tolerant: skip stray semicolons between statements
            if self.cur_token_is(SEMICOLON):
                self.next_token()
                continue

            stmt = self.parse_statement()
            if stmt:
                program.statements.append(stmt)

            self.next_token()
        return program

    def parse_statement(self):
        """Parse statements with clear error reporting"""
        try:
            if self.cur_token_is(LET):
                return self.parse_let_statement()
            elif self.cur_token_is(RETURN):
                return self.parse_return_statement()
            elif self.cur_token_is(PRINT):
                return self.parse_print_statement()
            elif self.cur_token_is(FOR):
                return self.parse_for_each_statement()
            elif self.cur_token_is(ACTION):
                return self.parse_action_statement()
            elif self.cur_token_is(IF):
                return self.parse_if_statement()
            elif self.cur_token_is(WHILE):
                return self.parse_while_statement()
            elif self.cur_token_is(USE):
                return self.parse_use_statement()
            elif self.cur_token_is(EXPORT):
                return self.parse_export_statement()
            elif self.cur_token_is(TRY):
                return self.parse_try_catch_statement()             # <-- new
            elif self.cur_token_is(EXTERNAL):
                return self.parse_external_declaration()            # <-- new
            else:
                return self.parse_expression_statement()
        except Exception as e:
            self.errors.append(f"Line {self.cur_token.line}: Parse error - {str(e)}")
            return None

    def parse_let_statement(self):
        """Fixed: Properly handles object literals"""
        if not self.expect_peek(IDENT):
            self.errors.append(f"Line {self.cur_token.line}: Expected variable name after 'let'")
            return None
            
        name = Identifier(self.cur_token.literal)
        
        if not self.expect_peek(ASSIGN):
            return None
            
        self.next_token()
        value = self.parse_expression(LOWEST)
        
        return LetStatement(name=name, value=value)

    def parse_map_literal(self):
        """FIXED: Proper map literal parsing - this was the core issue!"""
        pairs = []

        # Must be called when current token is LBRACE
        if not self.cur_token_is(LBRACE):
            self.errors.append(f"Line {getattr(self.cur_token, 'line', 'unknown')}: parse_map_literal called on non-brace token")
            return None

        # Move inside the braces
        self.next_token()  # advance to token after '{'

        # Handle empty object case: {}
        if self.cur_token_is(RBRACE):
            return MapLiteral(pairs)

        # Parse key-value pairs
        while not self.cur_token_is(RBRACE) and not self.cur_token_is(EOF):
            # Parse key (can be string or identifier)
            if self.cur_token_is(STRING):
                key = StringLiteral(self.cur_token.literal)
            elif self.cur_token_is(IDENT):
                key = Identifier(self.cur_token.literal)
            else:
                self.errors.append(f"Line {getattr(self.cur_token, 'line', 'unknown')}: Object key must be string or identifier")
                return None

            # Expect colon (current peek should be COLON)
            if not self.expect_peek(COLON):
                return None

            # Move to value token and parse it
            self.next_token()
            value = self.parse_expression(LOWEST)
            if value is None:
                return None

            pairs.append((key, value))

            # Accept comma OR semicolon as separators; tolerate trailing separators
            if self.peek_token_is(COMMA) or self.peek_token_is(SEMICOLON):
                self.next_token()  # move to separator
                # advance to next token after separator (or closing brace)
                if self.peek_token_is(RBRACE):
                    self.next_token()  # move to RBRACE and break next loop iteration
                    break
                self.next_token()
                continue

            # If closing brace is the next token, consume it and finish
            if self.peek_token_is(RBRACE):
                self.next_token()  # advance to RBRACE
                break

            # Otherwise, try to advance; tolerant parsing
            self.next_token()

        # Final check: should be at a RBRACE token
        if not self.cur_token_is(RBRACE):
            self.errors.append(f"Line {getattr(self.cur_token, 'line', 'unknown')}: Expected '}}' to close object literal")
            return None

        # Note: we keep the closing brace consumed (caller behavior consistent)
        return MapLiteral(pairs)

    # Rest of parser methods (simplified for production)
    def parse_expression(self, precedence):
        if self.cur_token.type not in self.prefix_parse_fns:
            self.errors.append(f"Line {self.cur_token.line}: Unexpected token '{self.cur_token.literal}'")
            return None

        prefix = self.prefix_parse_fns[self.cur_token.type]
        left_exp = prefix()

        if left_exp is None:
            return None

        while (not self.peek_token_is(SEMICOLON) and 
               not self.peek_token_is(EOF) and 
               precedence <= self.peek_precedence()):

            if self.peek_token.type not in self.infix_parse_fns:
                return left_exp

            infix = self.infix_parse_fns[self.peek_token.type]
            self.next_token()
            left_exp = infix(left_exp)

            if left_exp is None:
                return None

        return left_exp

    def parse_identifier(self):
        return Identifier(value=self.cur_token.literal)

    def parse_integer_literal(self):
        try:
            return IntegerLiteral(value=int(self.cur_token.literal))
        except ValueError:
            self.errors.append(f"Line {self.cur_token.line}: Could not parse {self.cur_token.literal} as integer")
            return None

    def parse_float_literal(self):
        try:
            return FloatLiteral(value=float(self.cur_token.literal))
        except ValueError:
            self.errors.append(f"Line {self.cur_token.line}: Could not parse {self.cur_token.literal} as float")
            return None

    def parse_string_literal(self):
        return StringLiteral(value=self.cur_token.literal)

    def parse_boolean(self):
        return Boolean(value=self.cur_token_is(TRUE))

    def parse_list_literal(self):
        elements = self.parse_expression_list(RBRACKET)
        return ListLiteral(elements=elements)

    def parse_grouped_expression(self):
        self.next_token()
        exp = self.parse_expression(LOWEST)
        if not self.expect_peek(RPAREN):
            return None
        return exp

    def parse_prefix_expression(self):
        expression = PrefixExpression(operator=self.cur_token.literal, right=None)
        self.next_token()
        expression.right = self.parse_expression(PREFIX)
        return expression

    def parse_infix_expression(self, left):
        expression = InfixExpression(left=left, operator=self.cur_token.literal, right=None)
        precedence = self.cur_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)
        return expression

    def parse_call_expression(self, function):
        arguments = self.parse_expression_list(RPAREN)
        return CallExpression(function=function, arguments=arguments)

    def parse_assignment_expression(self, left):
        if not isinstance(left, Identifier):
            self.errors.append(f"Line {self.cur_token.line}: Cannot assign to {type(left).__name__}")
            return None

        expression = AssignmentExpression(name=left, value=None)
        self.next_token()
        expression.value = self.parse_expression(LOWEST)
        return expression

    def parse_method_call_expression(self, left):
        if not self.expect_peek(IDENT):
            return None

        method = Identifier(self.cur_token.literal)

        if self.peek_token_is(LPAREN):
            self.next_token()
            arguments = self.parse_expression_list(RPAREN)
            return MethodCallExpression(object=left, method=method, arguments=arguments)
        else:
            return PropertyAccessExpression(object=left, property=method)

    def parse_expression_list(self, end):
        elements = []
        if self.peek_token_is(end):
            self.next_token()
            return elements

        self.next_token()
        elements.append(self.parse_expression(LOWEST))

        while self.peek_token_is(COMMA):
            self.next_token()
            self.next_token()
            elements.append(self.parse_expression(LOWEST))

        if not self.expect_peek(end):
            return elements

        return elements

    # Statement parsing methods
    def parse_return_statement(self):
        stmt = ReturnStatement(return_value=None)
        self.next_token()
        stmt.return_value = self.parse_expression(LOWEST)
        return stmt

    def parse_print_statement(self):
        stmt = PrintStatement(value=None)
        self.next_token()
        stmt.value = self.parse_expression(LOWEST)
        return stmt

    def parse_if_statement(self):
        self.next_token()  # Skip IF
        
        # Parse condition (with or without parentheses)
        if self.cur_token_is(LPAREN):
            self.next_token()
            condition = self.parse_expression(LOWEST)
            if self.cur_token_is(RPAREN):
                self.next_token()
        else:
            condition = self.parse_expression(LOWEST)

        if not condition:
            return None

        # Parse consequence
        consequence = self.parse_block()
        if not consequence:
            return None

        alternative = None
        if self.cur_token_is(ELSE):
            self.next_token()
            alternative = self.parse_block()

        return IfStatement(condition=condition, consequence=consequence, alternative=alternative)

    def parse_block(self):
        block = BlockStatement()

        # Handle different block styles
        if self.cur_token_is(LBRACE):
            self.next_token()  # Skip {

            while not self.cur_token_is(RBRACE) and not self.cur_token_is(EOF):
                # Skip stray semicolons between statements inside a block
                if self.cur_token_is(SEMICOLON):
                    self.next_token()
                    continue

                stmt = self.parse_statement()
                if stmt:
                    block.statements.append(stmt)

                # After parsing a statement, consume any trailing semicolons so they don't become unexpected tokens
                while self.peek_token_is(SEMICOLON):
                    self.next_token()  # move to semicolon
                    self.next_token()  # move past semicolon

                # Advance to next token if parser hasn't advanced to EOF or closing brace
                if not self.cur_token_is(RBRACE) and not self.cur_token_is(EOF):
                    self.next_token()

            if self.cur_token_is(EOF):
                self.errors.append("Unclosed block (reached EOF)")
        else:
            # Single statement block
            # Tolerant: allow a trailing semicolon after single statement
            stmt = self.parse_statement()
            if stmt:
                block.statements.append(stmt)
                if self.peek_token_is(SEMICOLON):
                    self.next_token()  # consume semicolon

        return block

    def parse_for_each_statement(self):
        if not self.expect_peek(EACH):
            return None
            
        if not self.expect_peek(IDENT):
            return None
            
        item = Identifier(self.cur_token.literal)
        
        if not self.expect_peek(IN):
            return None
            
        self.next_token()
        iterable = self.parse_expression(LOWEST)
        
        body = self.parse_block()
        
        return ForEachStatement(item=item, iterable=iterable, body=body)

    def parse_action_statement(self):
        if not self.expect_peek(IDENT):
            return None
            
        name = Identifier(self.cur_token.literal)
        
        parameters = []
        if self.peek_token_is(LPAREN):
            self.next_token()
            parameters = self.parse_parameter_list()
        
        body = self.parse_block()
        
        return ActionStatement(name=name, parameters=parameters, body=body)

    def parse_parameter_list(self):
        params = []
        if self.peek_token_is(RPAREN):
            self.next_token()
            return params

        self.next_token()
        if self.cur_token_is(IDENT):
            params.append(Identifier(self.cur_token.literal))

        while self.peek_token_is(COMMA):
            self.next_token()
            self.next_token()
            if self.cur_token_is(IDENT):
                params.append(Identifier(self.cur_token.literal))

        if not self.expect_peek(RPAREN):
            return None

        return params

    def parse_while_statement(self):
        if not self.expect_peek(LPAREN):
            return None
            
        self.next_token()
        condition = self.parse_expression(LOWEST)
        
        if not self.expect_peek(RPAREN):
            return None
            
        body = self.parse_block()
        
        return WhileStatement(condition=condition, body=body)

    def parse_use_statement(self):
        if not self.expect_peek(STRING):
            return None
            
        file_path = self.cur_token.literal
        
        alias = None
        if self.peek_token_is(IDENT) and self.peek_token.literal == "as":
            self.next_token()
            self.next_token()
            if self.cur_token_is(IDENT):
                alias = self.cur_token.literal
        
        return UseStatement(file_path=file_path, alias=alias)

    def parse_export_statement(self):
        if not self.expect_peek(IDENT):
            return None
            
        name = Identifier(self.cur_token.literal)
        return ExportStatement(name=name)

    def parse_expression_statement(self):
        expression = self.parse_expression(LOWEST)
        return ExpressionStatement(expression=expression)

    # Lambda and other expression types
    def parse_lambda_expression(self):
        parameters = []
        
        if self.cur_token_is(LPAREN):
            self.next_token()
            parameters = self.parse_parameter_list()
        elif self.cur_token_is(IDENT):
            parameters = [Identifier(self.cur_token.literal)]
            self.next_token()

        body = self.parse_expression(LOWEST)
        return LambdaExpression(parameters=parameters, body=body)

    def parse_action_literal(self):
        if not self.expect_peek(LPAREN):
            return None
            
        parameters = self.parse_parameter_list()
        if parameters is None:
            return None

        body = self.parse_expression(LOWEST)
        return ActionLiteral(parameters=parameters, body=body)

    def parse_if_expression(self):
        if not self.expect_peek(LPAREN):
            return None
            
        self.next_token()
        condition = self.parse_expression(LOWEST)
        
        if not self.expect_peek(RPAREN):
            return None
            
        if not self.expect_peek(LBRACE):
            return None
            
        consequence = self.parse_block()
        
        alternative = None
        if self.cur_token_is(ELSE):
            self.next_token()
            if not self.expect_peek(LBRACE):
                return None
            alternative = self.parse_block()

        return IfExpression(condition=condition, consequence=consequence, alternative=alternative)

    def parse_embedded_literal(self):
        # Simplified embedded literal parsing
        return EmbeddedLiteral(language="unknown", code="")

    # New: try-catch parsing
    def parse_try_catch_statement(self):
        """Basic try-catch parsing for production parser (more tolerant)"""
        # current token is TRY
        self.next_token()  # advance to what should be LBRACE or block indicator
        # parse try block (brace block preferred)
        try_block = self.parse_block()

        # Expect a CATCH
        if not self.cur_token_is(CATCH) and not self.peek_token_is(CATCH):
            self.errors.append(f"Line {getattr(self.cur_token, 'line', 'unknown')}: Expected 'catch' after try block")
            return None

        # ensure we're at CATCH
        if not self.cur_token_is(CATCH):
            self.next_token()

        # extract optional catch variable (tolerant handling)
        error_var = Identifier("error")

        # If next is parentheses, accept nested parentheses and find IDENT inside
        if self.peek_token_is(LPAREN):
            # move to first LPAREN
            self.next_token()  # now at LPAREN
            # advance inside parentheses, skip any extra '(' until IDENT or RPAREN encountered
            self.next_token()
            # Skip nested LPAREN until identifier or RPAREN
            while self.cur_token_is(LPAREN) and not self.cur_token_is(EOF):
                self.next_token()

            # If ident found, use it
            if self.cur_token_is(IDENT):
                error_var = Identifier(self.cur_token.literal)
                # consume remaining RPAREN tokens (tolerant)
                while self.peek_token_is(RPAREN):
                    self.next_token()
            else:
                # No identifier inside parens; default to "error" and try to position at next relevant token
                pass

        # catch <ident> style (no parens)
        elif self.peek_token_is(IDENT):
            self.next_token()
            if self.cur_token_is(IDENT):
                error_var = Identifier(self.cur_token.literal)

        # Move to the token that starts the catch block; tolerate optional tokens
        # If current token is RPAREN, advance one to reach the following token (often LBRACE)
        if self.cur_token_is(RPAREN) and not self.peek_token_is(EOF):
            self.next_token()

        # Ensure we're positioned to parse the catch block
        if not (self.cur_token_is(LBRACE) or self.peek_token_is(LBRACE)):
            # If next token is LBRACE, advance to it
            if self.peek_token_is(LBRACE):
                self.next_token()

        # parse catch block
        catch_block = self.parse_block()
        return TryCatchStatement(try_block=try_block, error_variable=error_var, catch_block=catch_block)

    # New: external declaration parsing
    def parse_external_declaration(self):
        """Parse: external action <name> from \"module\""""
        # current token is EXTERNAL
        if not self.expect_peek(ACTION):
            return None
        if not self.expect_peek(IDENT):
            return None
        name = Identifier(self.cur_token.literal)
        # optional parameter list like external action foo(param1, ...)
        parameters = []
        if self.peek_token_is(LPAREN):
            self.next_token()
            parameters = self.parse_parameter_list() or []
        if not self.expect_peek(FROM):
            self.errors.append(f"Line {getattr(self.cur_token, 'line', 'unknown')}: Expected 'from' in external declaration")
            return None
        if not self.expect_peek(STRING):
            self.errors.append(f"Line {getattr(self.cur_token, 'line', 'unknown')}: Expected module string in external declaration")
            return None
        module_path = self.cur_token.literal
        return ExternalDeclaration(name=name, parameters=parameters, module_path=module_path)

    # Token utilities
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def cur_token_is(self, t):
        return self.cur_token.type == t

    def peek_token_is(self, t):
        return self.peek_token.type == t

    def expect_peek(self, t):
        if self.peek_token_is(t):
            self.next_token()
            return True
        self.errors.append(f"Line {self.cur_token.line}: Expected '{t}', got '{self.peek_token.type}'")
        return False

    def peek_precedence(self):
        return precedences.get(self.peek_token.type, LOWEST)

    def cur_precedence(self):
        return precedences.get(self.cur_token.type, LOWEST)

# --- Compatibility alias ----------------------------------------------------
# Provide the common name `Parser` for code that imports the compiler parser
# using older/alternate names.
Parser = ProductionParser