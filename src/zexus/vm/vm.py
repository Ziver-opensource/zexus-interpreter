"""
Zexus Virtual Machine - Fast Bytecode Execution
"""

from ..object import (
    Environment, Integer, Float, String, Boolean as BooleanObj,
    List, Map, Null, Builtin
)

NULL = Null()
TRUE = BooleanObj(True)
FALSE = BooleanObj(False)

class ZexusVM:
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.environment = Environment()
        self.ip = 0  # Instruction pointer
        
        # Initialize builtins
        self.init_builtins()
    
    def init_builtins(self):
        # Add basic builtins to environment
        builtins = {
            'print': Builtin(lambda *args: self.builtin_print(*args), "print"),
            'len': Builtin(lambda *args: self.builtin_len(*args), "len"),
        }
        
        for name, builtin in builtins.items():
            self.environment.set(name, builtin)
    
    def execute(self):
        """Execute bytecode instructions"""
        try:
            while self.ip < len(self.bytecode.instructions):
                opcode, operand = self.bytecode.instructions[self.ip]
                self.execute_instruction(opcode, operand)
                self.ip += 1
                
            return self.stack.pop() if self.stack else NULL
            
        except Exception as e:
            return f"VM Error: {str(e)}"
    
    def execute_instruction(self, opcode, operand):
        if opcode == 'LOAD_CONST':
            constant = self.bytecode.constants[operand]
            self.stack.append(self.to_zexus_object(constant))
            
        elif opcode == 'LOAD':
            var_name = self.bytecode.constants[operand]
            value = self.environment.get(var_name)
            if value:
                self.stack.append(value)
            else:
                raise RuntimeError(f"Undefined variable: {var_name}")
                
        elif opcode == 'STORE':
            var_name = self.bytecode.constants[operand]
            value = self.stack.pop()
            self.environment.set(var_name, value)
            
        elif opcode == 'PRINT':
            value = self.stack.pop()
            print(value.inspect())
            
        elif opcode == 'ADD':
            right = self.stack.pop()
            left = self.stack.pop()
            result = self.add_objects(left, right)
            self.stack.append(result)
            
        elif opcode == 'SUB':
            right = self.stack.pop()
            left = self.stack.pop()
            result = self.sub_objects(left, right)
            self.stack.append(result)
            
        elif opcode == 'MUL':
            right = self.stack.pop()
            left = self.stack.pop()
            result = self.mul_objects(left, right)
            self.stack.append(result)
            
        elif opcode == 'DIV':
            right = self.stack.pop()
            left = self.stack.pop()
            result = self.div_objects(left, right)
            self.stack.append(result)
            
        elif opcode == 'EQ':
            right = self.stack.pop()
            left = self.stack.pop()
            result = self.eq_objects(left, right)
            self.stack.append(result)
            
        elif opcode == 'JUMP_IF_FALSE':
            condition = self.stack.pop()
            if not self.is_truthy(condition):
                self.ip = operand - 1  # -1 because ip will be incremented
                
        elif opcode == 'JUMP':
            self.ip = operand - 1  # -1 because ip will be incremented
            
        elif opcode == 'CALL':
            # Simplified function call
            func_name = self.bytecode.constants[operand]
            func = self.environment.get(func_name)
            if isinstance(func, Builtin):
                # Call builtin function
                arg_count = 0  # Simplified - would need to track actual args
                args = [self.stack.pop() for _ in range(arg_count)]
                result = func.fn(*args)
                self.stack.append(result)
    
    def to_zexus_object(self, value):
        if isinstance(value, int):
            return Integer(value)
        elif isinstance(value, float):
            return Float(value)
        elif isinstance(value, str):
            return String(value)
        elif isinstance(value, bool):
            return BooleanObj(value)
        else:
            return String(str(value))
    
    def is_truthy(self, obj):
        if obj == NULL or obj == FALSE:
            return False
        return True
    
    def add_objects(self, left, right):
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value + right.value)
        elif isinstance(left, Float) and isinstance(right, Float):
            return Float(left.value + right.value)
        elif isinstance(left, String) and isinstance(right, String):
            return String(left.value + right.value)
        else:
            return String(str(left) + str(right))
    
    def sub_objects(self, left, right):
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value - right.value)
        elif isinstance(left, Float) and isinstance(right, Float):
            return Float(left.value - right.value)
        else:
            raise RuntimeError("Unsupported types for subtraction")
    
    def mul_objects(self, left, right):
        if isinstance(left, Integer) and isinstance(right, Integer):
            return Integer(left.value * right.value)
        elif isinstance(left, Float) and isinstance(right, Float):
            return Float(left.value * right.value)
        else:
            raise RuntimeError("Unsupported types for multiplication")
    
    def div_objects(self, left, right):
        if isinstance(left, Integer) and isinstance(right, Integer):
            if right.value == 0:
                raise RuntimeError("Division by zero")
            return Integer(left.value // right.value)
        elif isinstance(left, Float) and isinstance(right, Float):
            if right.value == 0:
                raise RuntimeError("Division by zero")
            return Float(left.value / right.value)
        else:
            raise RuntimeError("Unsupported types for division")
    
    def eq_objects(self, left, right):
        if isinstance(left, Integer) and isinstance(right, Integer):
            return BooleanObj(left.value == right.value)
        elif isinstance(left, String) and isinstance(right, String):
            return BooleanObj(left.value == right.value)
        elif isinstance(left, BooleanObj) and isinstance(right, BooleanObj):
            return BooleanObj(left.value == right.value)
        else:
            return FALSE
    
    # Builtin functions
    def builtin_print(self, *args):
        for arg in args:
            print(arg.inspect())
        return NULL
    
    def builtin_len(self, *args):
        if len(args) != 1:
            return String("len() takes exactly 1 argument")
        
        arg = args[0]
        if isinstance(arg, String):
            return Integer(len(arg.value))
        elif isinstance(arg, List):
            return Integer(len(arg.elements))
        else:
            return String(f"len() not supported for {arg.type()}")