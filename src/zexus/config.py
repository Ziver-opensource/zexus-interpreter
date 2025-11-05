# src/zexus/config.py
"""
Enhanced Configuration system for Zexus Hybrid Architecture
"""

class ZexusConfig:
    def __init__(self):
        # Parser settings
        self.enable_advanced_parsing = True
        self.enable_debug_logs = False
        self.syntax_style = "universal"
        
        # Hybrid system settings
        self.use_hybrid_compiler = True
        self.fallback_to_interpreter = True
        self.enable_jit = False
        
        # Performance settings
        self.optimize_bytecode = True
        self.cache_compiled_code = False
        
        # Execution thresholds
        self.compiler_line_threshold = 100  # Use compiler for files > 100 lines
        self.enable_execution_stats = True
        
        # Compiler-specific settings
        self.enable_compiler_optimizations = True
    
    @classmethod
    def production(cls):
        """Production configuration - minimal logging, maximum performance"""
        config = cls()
        config.enable_debug_logs = False
        config.enable_advanced_parsing = False
        config.use_hybrid_compiler = True
        config.optimize_bytecode = True
        config.enable_execution_stats = False
        config.compiler_line_threshold = 50  # More aggressive compilation
        return config
    
    @classmethod
    def development(cls):
        """Development configuration - more verbose"""
        config = cls()
        config.enable_debug_logs = True
        config.enable_advanced_parsing = True
        config.use_hybrid_compiler = True  # Enable hybrid for testing
        config.enable_execution_stats = True
        return config
    
    @classmethod
    def performance(cls):
        """Performance configuration - always use compiler when possible"""
        config = cls()
        config.enable_debug_logs = False
        config.use_hybrid_compiler = True
        config.fallback_to_interpreter = False  # No fallback - fail if compiler fails
        config.compiler_line_threshold = 10  # Use compiler for even small files
        config.enable_compiler_optimizations = True
        return config
    
    @classmethod  
    def interpreter_only(cls):
        """Interpreter-only configuration"""
        config = cls()
        config.use_hybrid_compiler = False
        config.enable_debug_logs = True
        return config

# Global configuration instance
config = ZexusConfig.development()  # Default to development for now