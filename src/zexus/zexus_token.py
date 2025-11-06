# zexus_token.py (ENHANCED WITH PHASE 1 TOKENS)

# Special Tokens
ILLEGAL = "ILLEGAL"
EOF = "EOF"

# Identifiers + Literals
IDENT = "IDENT"
INT = "INT"
STRING = "STRING"
FLOAT = "FLOAT"

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
MOD = "%"
DOT = "."
LTE = "<="
GTE = ">="
AND = "&&"
OR = "||"

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
USE = "USE"
EXACTLY = "EXACTLY"
EMBEDDED = "EMBEDDED"
EXPORT = "EXPORT"
LAMBDA = "LAMBDA"
DEBUG = "DEBUG"      # NEW: Debug token
TRY = "TRY"          # NEW: Try token
CATCH = "CATCH"      # NEW: Catch token
EXTERNAL = "EXTERNAL" # NEW: External token
FROM = "FROM"        # NEW: From token

class Token:
    def __init__(self, token_type, literal, line=None, column=None):
        self.type = token_type
        self.literal = literal
        self.line = line  # ✅ ADD line tracking
        self.column = column  # ✅ ADD column tracking
        
        # For backward compatibility with code expecting dict-like tokens
        self.value = literal  # Alias for literal

    def __repr__(self):
        if self.line and self.column:
            return f"Token({self.type}, '{self.literal}', line={self.line}, col={self.column})"
        return f"Token({self.type}, '{self.literal}')"
    
    def get(self, key, default=None):
        """Dict-like get method for backward compatibility"""
        if hasattr(self, key):
            return getattr(self, key)
        return default
    
    def __getitem__(self, key):
        """Allow dict-like access for compatibility"""
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"Token has no attribute '{key}'")
    
    def __contains__(self, key):
        """Check if token has attribute"""
        return hasattr(self, key)
    
    def to_dict(self):
        """Convert token to dictionary for compatibility"""
        return {
            'type': self.type,
            'literal': self.literal,
            'value': self.literal,
            'line': self.line,
            'column': self.column
        }