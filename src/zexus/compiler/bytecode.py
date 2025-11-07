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
                
"""
Simple Bytecode Generator for Zexus compiler frontend.

This generator emits a linear list of ops (tuples) that represent
high-level actions. The VM or further stages can convert ops into
real instructions. The format is intentionally simple:

- ("DEFINE_SCREEN", name, properties_dict)
- ("DEFINE_COMPONENT", name, properties_dict)
- ("DEFINE_THEME", name, properties_dict)
- ("CALL_BUILTIN", name, [arg1, arg2, ...])
- ("LET", name, value_op)  # value_op can be a literal or nested op
- ("EXPR", expr_op)        # placeholder for expressions
- etc.

This generator focuses on renderer-related constructs and a few common statements.
"""
from ..zexus_ast import Program, ExpressionStatement, BlockStatement, LetStatement, MapLiteral, StringLiteral, IntegerLiteral, ListLiteral, Identifier, CallExpression
from typing import List, Any, Dict

class BytecodeGenerator:
	def __init__(self):
		self.ops: List[tuple] = []

	def generate(self, program: Program) -> List[tuple]:
		self.ops = []
		for stmt in getattr(program, "statements", []):
			self._emit_statement(stmt)
		return self.ops

	def _emit_statement(self, stmt):
		typ = type(stmt).__name__
		if typ == "LetStatement":
			name = stmt.name.value if hasattr(stmt.name, 'value') else str(stmt.name)
			value = self._emit_expression_like(stmt.value)
			self.ops.append(("LET", name, value))
		elif typ == "ExpressionStatement":
			self.ops.append(("EXPR", self._emit_expression_like(stmt.expression)))
		elif typ == "ScreenStatement":
			name = stmt.name.value if hasattr(stmt.name, 'value') else str(stmt.name)
			props = self._emit_block_properties(stmt.body)
			self.ops.append(("DEFINE_SCREEN", name, props))
		elif typ == "ComponentStatement":
			name = stmt.name.value if hasattr(stmt.name, 'value') else str(stmt.name)
			props = self._emit_block_properties(stmt.properties)
			self.ops.append(("DEFINE_COMPONENT", name, props))
		elif typ == "ThemeStatement":
			name = stmt.name.value if hasattr(stmt.name, 'value') else str(stmt.name)
			props = self._emit_block_properties(stmt.properties)
			self.ops.append(("DEFINE_THEME", name, props))
		else:
			# Fallback: try to handle common statements as generic expression
			if hasattr(stmt, "expression"):
				self.ops.append(("EXPR", self._emit_expression_like(getattr(stmt, "expression", None))))
			else:
				self.ops.append(("NOP", typ))

	def _emit_block_properties(self, block):
		# block may be a MapLiteral or BlockStatement (tolerant). Return a python dict.
		if isinstance(block, MapLiteral):
			return self._mapliteral_to_dict(block)
		if isinstance(block, BlockStatement):
			props = {}
			for s in block.statements:
				# Attempt to extract simple key: value from statements (best-effort)
				if isinstance(s, ExpressionStatement):
					expr = s.expression
					# handle simple "key: value" represented as MapLiteral inside expression
					# (Compiler grammar should ensure map-literals for property blocks)
				# ignore unknowns
			return props
		# unknown node: return empty
		return {}

	def _mapliteral_to_dict(self, maplit: MapLiteral) -> Dict[str, Any]:
		result = {}
		for k_expr, v_expr in maplit.pairs:
			# k_expr is likely Identifier or StringLiteral
			key = getattr(k_expr, 'value', str(k_expr))
			val = self._emit_expression_like(v_expr)
			if isinstance(val, tuple) and val[0] == "LITERAL":
				result[key] = val[1]
			else:
				result[key] = val
		return result

	def _emit_expression_like(self, expr):
		# Emit a simple representation for literals and calls
		if expr is None:
			return ("LITERAL", None)
		typ = type(expr).__name__
		if typ == "StringLiteral":
			return ("LITERAL", expr.value)
		if typ == "IntegerLiteral":
			return ("LITERAL", expr.value)
		if typ == "FloatLiteral":
			return ("LITERAL", expr.value)
		if typ == "Boolean":
			return ("LITERAL", expr.value)
		if typ == "Identifier":
			return ("IDENT", expr.value)
		if typ == "CallExpression":
			func = expr.function
			func_name = getattr(func, 'value', None)
			args = [self._emit_expression_like(a) for a in expr.arguments]
			return ("CALL_BUILTIN", func_name, args)
		if typ == "MapLiteral":
			return ("MAP", self._mapliteral_to_dict(expr))
		if typ == "ListLiteral":
			return ("LIST", [self._emit_expression_like(e) for e in expr.elements])
		# fallback
		return ("EXPR", typ)

# Backwards compatibility
Generator = BytecodeGenerator