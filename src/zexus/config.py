# src/zexus/config.py
"""
Configuration system for Zexus Hybrid Architecture
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
    
    @classmethod
    def production(cls):
        """Production configuration - minimal logging, maximum performance"""
        config = cls()
        config.enable_debug_logs = False
        config.enable_advanced_parsing = False  # Use simple parser in production
        config.use_hybrid_compiler = True
        config.optimize_bytecode = True
        return config
    
    @classmethod
    def development(cls):
        """Development configuration - more verbose"""
        config = cls()
        config.enable_debug_logs = True
        config.enable_advanced_parsing = True
        config.use_hybrid_compiler = False  # Use interpreter for debugging
        return config

# Global configuration instance
config = ZexusConfig.production()  # Default to production mode