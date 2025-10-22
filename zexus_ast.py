# ast.py (Updated for Actions)

# Base classes
class Node: pass
class Statement(Node): pass
class Expression(Node): pass

class Program(Node):
    def __init__(self):
        self.statements = []

# Statement Nodes
class LetStatement(Statement):
    def __init__(self, name, value): self.name = name; self.value = value

class ReturnStatement(Statement): # NEW
    def __init__(self, return_value):
        self.return_value = return_value

class ExpressionStatement(Statement):
    def __init__(self, expression): self.expression = expression

class BlockStatement(Statement):
    def __init__(self): self.statements = []

class PrintStatement(Statement):
    def __init__(self, value): self.value = value

class ForEachStatement(Statement):
    def __init__(self, item, iterable, body):
        self.item = item; self.iterable = iterable; self.body = body

# Add these new AST nodes to zexus_ast.py

# NEW: If statement node (different from IfExpression)
class IfStatement(Statement):
    def __init__(self, condition, consequence, alternative=None):
        self.condition = condition
        self.consequence = consequence  # BlockStatement
        self.alternative = alternative  # BlockStatement or IfStatement (for else if)

# NEW: While loop node
class WhileStatement(Statement):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body  # BlockStatement

# NEW: Node for a 'screen' declaration
class ScreenStatement(Statement):
    def __init__(self, name, body):
        self.name = name # The Identifier for the screen name
        self.body = body # The BlockStatement for the screen's content

# NEW: Node for an 'action' declaration
class ActionStatement(Statement):
    def __init__(self, name, parameters, body):
        self.name = name # The Identifier for the function name
        self.parameters = parameters # List of Identifiers
        self.body = body # The BlockStatement for the function body

# Expression Nodes
class Identifier(Expression):
    def __init__(self, value): self.value = value

class IntegerLiteral(Expression):
    def __init__(self, value): self.value = value

class FloatLiteral(Expression):
    def __init__(self, value): self.value = value

class StringLiteral(Expression):
    def __init__(self, value): self.value = value

class Boolean(Expression):
    def __init__(self, value): self.value = value

class ListLiteral(Expression):
    def __init__(self, elements): self.elements = elements

class MapLiteral(Expression):
    def __init__(self, pairs): self.pairs = pairs  # List of (key, value) tuples

class ActionLiteral(Expression): # NEW
    def __init__(self, parameters, body):
        self.parameters = parameters
        self.body = body

class CallExpression(Expression): # NEW
    def __init__(self, function, arguments):
        self.function = function # Identifier or ActionLiteral
        self.arguments = arguments

class PrefixExpression(Expression):
    def __init__(self, operator, right): self.operator = operator; self.right = right

class InfixExpression(Expression):
    def __init__(self, left, operator, right): self.left = left; self.operator = operator; self.right = right

class IfExpression(Expression):
    def __init__(self, condition, consequence, alternative=None):
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative
