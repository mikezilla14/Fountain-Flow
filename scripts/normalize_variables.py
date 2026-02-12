"""
Variable normalization utility for FFlow.

Ensures all variable references use the mandatory $ prefix for
compatibility with transpilation targets and roundtrip fidelity.
"""

import re
from typing import Set


class VariableNormalizer:
    """Normalizes FFlow variable references to use mandatory $ prefix."""
    
    # Reserved keywords that should NOT get $ prefix
    RESERVED = {'true', 'false', 'null', 'random', 'and', 'or', 'not'}
    
    def normalize_expression(self, expr: str) -> str:
        """
        Add $ prefix to variables in expressions that don't have it.
        
        Args:
            expr: Expression to normalize (e.g., "player.hp += 5")
            
        Returns:
            Normalized expression (e.g., "$player.hp += 5")
        """
        result = []
        i = 0
        
        while i < len(expr):
            ch = expr[i]
            
            # Check if we're at the start of an identifier
            if ch.isalpha() or ch == '_':
                # Look back to see if there's already a $
                has_dollar = (i > 0 and expr[i-1] == '$')
                
                # Collect the full identifier (including dots for paths)
                j = i
                while j < len(expr) and (expr[j].isalnum() or expr[j] in '_.'):
                    j += 1
                
                identifier = expr[i:j]
                
                # Check if this is a function call (identifier followed by '(')
                k = j
                while k < len(expr) and expr[k].isspace():
                    k += 1
                is_function = (k < len(expr) and expr[k] == '(')
                
                # Check if it's a reserved word
                base_identifier = identifier.split('.')[0]
                is_reserved = base_identifier.lower() in self.RESERVED
                
                # Add $ prefix if not already there, not a function, and not reserved
                if not has_dollar and not is_function and not is_reserved:
                    result.append('$')
                result.append(identifier)
                i = j
            else:
                result.append(ch)
                i += 1
        
        return ''.join(result)
    
    def normalize_fflow_file(self, content: str) -> str:
        """
        Normalize all variable references in a FFlow file.
        
        Args:
            content: FFlow file content
            
        Returns:
            Normalized content with $ prefixes added
        """
        lines = content.split('\n')
        normalized_lines = []
        
        for line in lines:
            # Skip frontmatter and empty lines
            if line.strip() in ['', '==='] or line.startswith('$$') or (line.strip().startswith('$') and ':' in line):
                normalized_lines.append(line)
                continue
            
            # Normalize state changes: ~ expression
            if match := re.match(r'^(\s*~\s+)(.+)$', line):
                indent = match.group(1)
                expr = match.group(2)
                normalized_lines.append(indent + self.normalize_expression(expr))
                continue
            
            # Normalize conditionals: (IF: condition), (ELIF: condition)
            if match := re.match(r'^(\s*\((?:IF|ELIF):\s+)(.+)(\).*)$', line):
                prefix = match.group(1)
                condition = match.group(2)
                suffix = match.group(3)
                normalized_lines.append(prefix + self.normalize_expression(condition) + suffix)
                continue
            
            # Normalize inline text expressions: $variable or ${expression}
            # This is for text like "Your HP is $player.hp"
            # Already has $, so skip
            
            normalized_lines.append(line)
        
        return '\n'.join(normalized_lines)


def normalize_file(input_path: str, output_path: str = None) -> None:
    """
    Normalize a FFlow file to use mandatory $ prefixes.
    
    Args:
        input_path: Path to input .fflow file
        output_path: Path to output file (defaults to overwriting input)
    """
    normalizer = VariableNormalizer()
    
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    normalized = normalizer.normalize_fflow_file(content)
    
    output_path = output_path or input_path
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(normalized)
    
    print(f"Normalized {input_path} -> {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python normalize_variables.py <input.fflow> [output.fflow]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    normalize_file(input_file, output_file)
