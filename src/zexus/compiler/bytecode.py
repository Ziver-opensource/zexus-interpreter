"""
Bytecode Generator for Zexus VM
"""

class Bytecode:
    def __init__(self):
        self.instructions = []
        self.constants = []
        
    def add_instruction(self, opcode, operand=None):
        self.instructions.append((opcode, operand))
        
    def add_constant(self, value):
        index = len(self.constants)
        self.constants.append(value)
        return index

class BytecodeGenerator:
    def __init__(self):
        self.bytecode = Bytecode()
        
    def generate(self, ast):
        """Generate bytecode from AST"""
        self.bytecode = Bytecode()
        self.generate_program(ast)
        return self.bytecode
    
    def generate_program(self, program):
        for stmt in program.statements:
            self.generate_statement(stmt)
    
    def generate_statement(self, stmt):
        from .zexus_ast import (
            LetStatement, ExpressionStatement, PrintStatement,
            ReturnStatement, IfStatement, WhileStatement
        )
        
        if isinstance(stmt, LetStatement):
            self.generate_let_statement(stmt)
        elif isinstance(stmt, ExpressionStatement):
            self.generate_expression(stmt.expression)
        elif isinstance(stmt, PrintStatement):
            self.generate_expression(stmt.value)
            self.bytecode.add_instruction('PRINT')
        elif isinstance(stmt, ReturnStatement):
            self.generate_expression(stmt.return_value)
            self.bytecode.add_instruction('RETURN')
        elif isinstance(stmt, IfStatement):
            self.generate_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self.generate_while_statement(stmt)
    
    def generate_let_statement(self, stmt):
        self.generate_expression(stmt.value)
        var_index = self.bytecode.add_constant(stmt.name.value)
        self.bytecode.add_instruction('STORE', var_index)
    
    def generate_if_statement(self, stmt):
        # Generate condition
        self.generate_expression(stmt.condition)
        
        # Jump if false
        jump_pos = len(self.bytecode.instructions)
        self.bytecode.add_instruction('JUMP_IF_FALSE', 0)  # placeholder
        
        # Generate consequence
        self.generate_statement(stmt.consequence)
        
        # Update jump position
        end_pos = len(self.bytecode.instructions)
        self.bytecode.instructions[jump_pos] = ('JUMP_IF_FALSE', end_pos)
    
    def generate_while_statement(self, stmt):
        start_pos = len(self.bytecode.instructions)
        
        # Generate condition
        self.generate_expression(stmt.condition)
        
        # Jump if false to end
        jump_pos = len(self.bytecode.instructions)
        self.bytecode.add_instruction('JUMP_IF_FALSE', 0)  # placeholder
        
        # Generate body
        self.generate_statement(stmt.body)
        
        # Jump back to condition
        self.bytecode.add_instruction('JUMP', start_pos)
        
        # Update jump position
        end_pos = len(self.bytecode.instructions)
        self.bytecode.instructions[jump_pos] = ('JUMP_IF_FALSE', end_pos)
    
    def generate_expression(self, expr):
        from .zexus_ast import (
            Identifier, IntegerLiteral, StringLiteral, Boolean,
            InfixExpression, PrefixExpression, CallExpression
        )
        
        if isinstance(expr, Identifier):
            var_index = self.bytecode.add_constant(expr.value)
            self.bytecode.add_instruction('LOAD', var_index)
            
        elif isinstance(expr, IntegerLiteral):
            const_index = self.bytecode.add_constant(expr.value)
            self.bytecode.add_instruction('LOAD_CONST', const_index)
            
        elif isinstance(expr, StringLiteral):
            const_index = self.bytecode.add_constant(expr.value)
            self.bytecode.add_instruction('LOAD_CONST', const_index)
            
        elif isinstance(expr, Boolean):
            const_index = self.bytecode.add_constant(expr.value)
            self.bytecode.add_instruction('LOAD_CONST', const_index)
            
        elif isinstance(expr, InfixExpression):
            self.generate_expression(expr.left)
            self.generate_expression(expr.right)
            
            # Add operator instruction
            op_map = {
                '+': 'ADD',
                '-': 'SUB',
                '*': 'MUL', 
                '/': 'DIV',
                '==': 'EQ',
                '!=': 'NEQ',
                '<': 'LT',
                '>': 'GT',
                '<=': 'LTE',
                '>=': 'GTE',
                '&&': 'AND',
                '||': 'OR'
            }
            opcode = op_map.get(expr.operator, 'UNKNOWN_OP')
            self.bytecode.add_instruction(opcode)
            
        elif isinstance(expr, PrefixExpression):
            self.generate_expression(expr.right)
            if expr.operator == '!':
                self.bytecode.add_instruction('NOT')
            elif expr.operator == '-':
                self.bytecode.add_instruction('NEG')
                
        elif isinstance(expr, CallExpression):
            # Generate arguments
            for arg in expr.arguments:
                self.generate_expression(arg)
                
            # Generate function call
            if isinstance(expr.function, Identifier):
                func_index = self.bytecode.add_constant(expr.function.value)
                self.bytecode.add_instruction('CALL', func_index)