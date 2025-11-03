"""
Bytecode Definitions for Zexus VM
"""

class Bytecode:
    def __init__(self):
        self.instructions = []
        self.constants = []
        
    def __repr__(self):
        return f"Bytecode({len(self.instructions)} instructions, {len(self.constants)} constants)"