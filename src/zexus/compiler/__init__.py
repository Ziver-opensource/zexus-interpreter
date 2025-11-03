# src/zexus/compiler/__init__.py

"""
Zexus Compiler Phase - Frontend compilation with semantic analysis
"""

from .lexer import Lexer
from .parser import ProductionParser
from .semantic import SemanticAnalyzer
from .bytecode import BytecodeGenerator
from .zexus_ast import *

class ZexusCompiler:
    def __init__(self, source, enable_optimizations=True):
        self.source = source
        self.enable_optimizations = enable_optimizations
        self.ast = None
        self.bytecode = None
        self.errors = []
        
    def compile(self):
        """Full compilation pipeline with enhanced error reporting"""
        try:
            # Phase 1: Lexical Analysis
            lexer = Lexer(self.source)
            
            # Phase 2: Syntax Analysis 
            parser = ProductionParser(lexer)
            self.ast = parser.parse_program()
            self.errors.extend(parser.errors)
            
            if self.errors:
                return None
                
            # Phase 3: Semantic Analysis
            analyzer = SemanticAnalyzer()
            semantic_errors = analyzer.analyze(self.ast)
            self.errors.extend(semantic_errors)
            
            if self.errors:
                return None
                
            # Phase 4: Bytecode Generation
            generator = BytecodeGenerator()
            self.bytecode = generator.generate(self.ast)
            
            return self.bytecode
            
        except Exception as e:
            self.errors.append(f"Compilation error: {str(e)}")
            return None
    
    def get_errors(self):
        """Get formatted error messages with line numbers"""
        return self.errors