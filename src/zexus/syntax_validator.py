# syntax_validator.py
class SyntaxValidator:
    def __init__(self):
        self.suggestions = []
        self.warnings = []
        
    def validate_code(self, code, desired_style="universal"):
        """Validate code and suggest improvements for the desired syntax style"""
        self.suggestions = []
        self.warnings = []
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            self._validate_line(line, line_num, desired_style)
            
        return {
            'is_valid': len(self.suggestions) == 0,
            'suggestions': self.suggestions,
            'warnings': self.warnings,
            'error_count': len(self.suggestions)
        }
    
    def _validate_line(self, line, line_num, style):
        """Validate a single line against the desired style"""
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith('#'):
            return
            
        # Universal style validations
        if style == "universal":
            self._validate_universal_syntax(stripped_line, line_num, line)
        # Tolerable style validations  
        elif style == "tolerable":
            self._validate_tolerable_syntax(stripped_line, line_num, line)
            
        # Common validations for both styles
        self._validate_common_syntax(stripped_line, line_num, line)
    
    def _validate_universal_syntax(self, stripped_line, line_num, original_line):
        """Validate against universal syntax rules"""
        # Check for colon blocks (should use braces)
        if (any(stripped_line.startswith(keyword) for keyword in ['if', 'for each', 'while', 'action', 'try']) 
            and stripped_line.endswith(':')):
            self.suggestions.append({
                'line': line_num,
                'message': "Universal syntax requires braces {} instead of colon for blocks",
                'fix': original_line.rstrip(':') + " {",
                'severity': 'warning'
            })
        
        # Check debug statements
        if stripped_line.startswith('debug ') and not stripped_line.startswith('debug('):
            self.suggestions.append({
                'line': line_num,
                'message': "Use parentheses with debug statements: debug(expression)",
                'fix': original_line.replace('debug ', 'debug(', 1) + ')',
                'severity': 'error'
            })
            
        # Check lambda syntax
        if 'lambda' in stripped_line and 'lambda ' in stripped_line and not 'lambda(' in stripped_line:
            self.suggestions.append({
                'line': line_num,
                'message': "Use parentheses with lambda parameters: lambda(params) -> expression",
                'fix': self._fix_lambda_syntax(original_line),
                'severity': 'error'
            })
            
        # Check catch without parentheses
        if 'catch' in stripped_line and 'catch ' in stripped_line and not 'catch(' in stripped_line:
            self.suggestions.append({
                'line': line_num,
                'message': "Use parentheses with catch: catch(error) { }",
                'fix': original_line.replace('catch ', 'catch(', 1).replace(' {', ') {'),
                'severity': 'error'
            })
    
    def _validate_tolerable_syntax(self, stripped_line, line_num, original_line):
        """Validate against tolerable syntax rules"""
        # Check for potentially confusing syntax
        if stripped_line.count('{') != stripped_line.count('}'):
            self.warnings.append({
                'line': line_num,
                'message': "Mismatched braces - this can cause parsing issues",
                'severity': 'warning'
            })
            
        # Check for mixed block styles in same context
        if (any(stripped_line.startswith(keyword) for keyword in ['if', 'for each', 'while']) 
            and ':' in stripped_line and '{' in stripped_line):
            self.suggestions.append({
                'line': line_num,
                'message': "Mixed block syntax - prefer consistent use of : or {}",
                'fix': original_line,
                'severity': 'warning'
            })
    
    def _validate_common_syntax(self, stripped_line, line_num, original_line):
        """Common validations for both syntax styles"""
        # Check for missing parentheses in function calls
        if (any(stripped_line.startswith(keyword) for keyword in ['if', 'while']) 
            and '(' not in stripped_line and not stripped_line.endswith(':')):
            self.suggestions.append({
                'line': line_num,
                'message': "Consider using parentheses for clarity: if (condition)",
                'fix': self._add_parentheses_to_condition(original_line),
                'severity': 'suggestion'
            })
            
        # Check for assignment in conditions (common bug)
        if 'if' in stripped_line and ' = ' in stripped_line and ' == ' not in stripped_line:
            self.warnings.append({
                'line': line_num,
                'message': "Possible assignment in condition - did you mean '=='?",
                'severity': 'warning'
            })
    
    def _fix_lambda_syntax(self, line):
        """Fix lambda syntax to universal style"""
        if 'lambda ' in line:
            # Simple case: lambda x: expr -> lambda(x) -> expr
            if ':' in line:
                return line.replace('lambda ', 'lambda(', 1).replace(':', ') ->', 1)
            # Case with arrow: lambda x -> expr -> lambda(x) -> expr
            elif '->' in line:
                return line.replace('lambda ', 'lambda(', 1).replace(' ->', ') ->', 1)
        return line
    
    def _add_parentheses_to_condition(self, line):
        """Add parentheses around condition"""
        if line.startswith('if '):
            return line.replace('if ', 'if (', 1) + ')'
        elif line.startswith('while '):
            return line.replace('while ', 'while (', 1) + ')'
        return line
    
    def auto_fix(self, code, desired_style="universal"):
        """Attempt to automatically fix syntax issues"""
        validation = self.validate_code(code, desired_style)
        
        if validation['is_valid']:
            return code, validation
            
        lines = code.split('\n')
        fixed_lines = lines.copy()
        applied_fixes = 0
        
        for suggestion in validation['suggestions']:
            if suggestion['severity'] in ['error', 'warning']:  # Only auto-fix errors and warnings
                line_num = suggestion['line'] - 1
                if line_num < len(fixed_lines):
                    fixed_lines[line_num] = suggestion['fix']
                    applied_fixes += 1
        
        fixed_code = '\n'.join(fixed_lines)
        
        # Re-validate after fixes
        final_validation = self.validate_code(fixed_code, desired_style)
        final_validation['applied_fixes'] = applied_fixes
        
        return fixed_code, final_validation
    
    def suggest_syntax_style(self, code):
        """Analyze code and suggest which syntax style it follows"""
        lines = code.split('\n')
        
        universal_indicators = 0
        tolerable_indicators = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # Universal indicators
            if any(stripped.startswith(kw + '(') for kw in ['if', 'while', 'debug']):
                universal_indicators += 1
            if 'lambda(' in stripped:
                universal_indicators += 1
            if stripped.endswith('{'):
                universal_indicators += 1
                
            # Tolerable indicators
            if any(stripped.startswith(kw + ' ') and stripped.endswith(':') 
                   for kw in ['if', 'for each', 'while', 'action']):
                tolerable_indicators += 1
            if 'debug ' in stripped and not stripped.startswith('debug('):
                tolerable_indicators += 1
            if 'lambda ' in stripped and not 'lambda(' in stripped:
                tolerable_indicators += 1
        
        if universal_indicators > tolerable_indicators:
            return "universal"
        elif tolerable_indicators > universal_indicators:
            return "tolerable"
        else:
            return "mixed"