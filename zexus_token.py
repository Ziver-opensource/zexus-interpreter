# token.py (Updated for Lists and Loops)

# This file defines all the possible token types in the Zexus language.

# Special Tokens
ILLEGAL = "ILLEGAL"
EOF = "EOF"

# Identifiers + Literals
IDENT = "IDENT"
INT = "INT"
STRING = "STRING" # Added from last update
FLOAT = "FLOAT" # New
# Operators
ASSIGN = "="
PLUS = "+"
MINUS = "-"
SLASH = "/"
STAR = "*"
BANG = "!"
LT = "<"
GT = ">"
EQ = "=="
NOT_EQ = "!="

# Delimiters
COMMA = ","
SEMICOLON = ";"
COLON = ":"
LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"
LBRACKET = "["
RBRACKET = "]"

# Keywords
LET = "LET"
PRINT = "PRINT"
IF = "IF"
ELSE = "ELSE"
RETURN = "RETURN"
TRUE = "TRUE"
FALSE = "FALSE"
FOR = "FOR"
EACH = "EACH"
IN = "IN"
ACTION = "ACTION"
SCREEN = "SCREEN"
MAP = "MAP"
WHILE = "WHILE"
# The Token class represents a single token, holding its type and value.
class Token:
    def __init__(self, token_type, literal):
        self.type = token_type
        self.literal = literal

    def __repr__(self):
        return f"Token({self.type}, '{self.literal}')"
