"""
Reverse parsers - Parse various formats back into FFlow AST.

This module provides parsers for Twee and Ren'Py formats, using the new
language-based architecture for consistency and maintainability.
"""

import re
from typing import List, Optional
from ..core.ast_nodes import (
    ScriptNode, ScriptAST, FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)
from .engine import GenericParser
from ..languages.twee import TweeLanguage
from ..languages.renpy import RenPyLanguage


class TweeParser:
    """
    Parses Twee (SugarCube) text into FFlow AST.
    
    Wrapper around GenericParser with TweeLanguage for backward compatibility.
    """
    
    # Legacy regex patterns - kept for reference
    REGEX_PASSAGE = r'^::\s*(.+)'
    REGEX_MACRO_SET = r'<<set\s+\$([\w.]+)\s*(to|=|\+=|-=|\*=|/=)\s*(.+)>>'
    REGEX_MACRO_IF = r'<<if\s+(.+)>>'
    REGEX_MACRO_ELSE = r'<<else>>'
    REGEX_MACRO_ENDIF = r'<<endif>>'
    REGEX_LINK = r'\[\[(.*?)(?:\|(.*?))?\]\]'
    REGEX_MACRO_GOTO = r'<<goto\s+"(.+)">>'
    REGEX_MACRO_BG = r'<<bg\s+"(.+)">>'
    REGEX_MACRO_SHOW = r'<<show\s+"(.+)">>'
    REGEX_MACRO_RUN = r'<<run\s+(.+)>>'
    REGEX_MACRO_AUDIO = r'<<audio\s+"(.+)"\s+play>>'
    REGEX_ELIF = r'<<elseif\s+(.+)>>'
    
    def __init__(self):
        self._parser = GenericParser(TweeLanguage())
    
    def _strip_vars(self, expr: str) -> str:
        """Remove $ from all variables for FFlow format."""
        # Remove $ prefix from all variable references
        # Matches $varname, $object.property, $_localvar
        return re.sub(r'\$([a-zA-Z_][\w.]*)', r'\1', expr)
    
    def parse(self, text: str) -> ScriptAST:
        """
        Parse Twee text into FFlow AST.
        
        Special handling: Convert :: StoryInit passage with <<set>> macros
        into a FrontmatterNode for proper FFlow representation.
        
        Args:
            text: Twee/SugarCube formatted text
            
        Returns:
            FFlow AST
        """
        # Parse with generic parser first
        ast = self._parser.parse(text)
        
        # Post-process: Convert StoryInit passage into FrontmatterNode
        if len(ast) > 0:
            # Check if first node is StoryInit section
            if (isinstance(ast[0], SectionHeadingNode) and 
                ast[0].text == "StoryInit"):
                
                # Collect all StateChangeNodes that follow until next section
                frontmatter_vars = {}
                nodes_to_remove = [0]  # Remove StoryInit heading
                
                i = 1
                while i < len(ast) and not isinstance(ast[i], SectionHeadingNode):
                    if isinstance(ast[i], StateChangeNode):
                        # Parse the set expression to extract variable assignment
                        # Format: "$varname = { ... }" or "varname = value"
                        expr = ast[i].expression
                        if '=' in expr:
                            parts = expr.split('=', 1)
                            var_name = parts[0].strip()
                            var_value = parts[1].strip()
                            
                            # Strip $ prefix from variable name for frontmatter format
                            if var_name.startswith('$'):
                                var_name = var_name[1:]
                            
                            # Try to evaluate object literals
                            if var_value.startswith('{') and var_value.endswith('}'):
                                # Parse object literal {key: val, ...}
                                obj_dict = {}
                                content = var_value[1:-1].strip()
                                if content:
                                    # Simple parsing - split by comma
                                    pairs = content.split(',')
                                    for pair in pairs:
                                        if ':' in pair:
                                            k, v = pair.split(':', 1)
                                            k = k.strip()
                                            # Strip quotes more thoroughly
                                            v = v.strip()
                                            # Remove both outer quotes and escaped quotes
                                            if v.startswith('"') and v.endswith('"'):
                                                v = v[1:-1]
                                            elif v.startswith("'") and v.endswith("'"):
                                                v = v[1:-1]
                                            obj_dict[k] = v
                                frontmatter_vars[var_name] = obj_dict
                            else:
                                # Simple value
                                frontmatter_vars[var_name] = var_value.strip('\'"')
                        
                        
                        nodes_to_remove.append(i)
                    i += 1
                
                # Create FrontmatterNode and replace the StoryInit section
                if frontmatter_vars:
                    fm_node = FrontmatterNode(variables=frontmatter_vars, depth=0)
                    # Remove nodes in reverse order to preserve indices
                    for idx in reversed(nodes_to_remove):
                        del ast[idx]
                    # Insert frontmatter at the beginning
                    ast.insert(0, fm_node)
        
        # NOTE: We intentionally do NOT merge ActionNode + JumpNode here
        # because in Twee, "text\n<<goto>>" is the correct representation
        # of FFlow's "text -> #target". The slight AST difference is acceptable
        # for cross-format compatibility.
        
        return ast


class RenPyParser:
    """
    Parses Ren'Py script into FFlow AST.
    
    Wrapper around GenericParser with RenPyLanguage for backward compatibility.
    """
    
    # Legacy regex patterns - kept for reference
    REGEX_LABEL = r'^label\s+(\w+):'
    REGEX_VAR = r'^\$\s*(\w+)\s*=\s*(.+)'
    REGEX_SCENE = r'^scene\s+(.+)'
    REGEX_SHOW = r'^show\s+(.+)'
    REGEX_MENU = r'^menu:'
    REGEX_JUMP = r'^jump\s+(\w+)'
    REGEX_IF = r'^if\s+(.+):'
    REGEX_ELSE = r'^else:'
    REGEX_DIALOGUE = r'^(\w+)\s+"(.+)"'
    REGEX_ACTION = r'^"(.+)"'
    
    def __init__(self):
        self._parser = GenericParser(RenPyLanguage())
    
    def parse(self, text: str) -> ScriptAST:
        """
        Parse Ren'Py script into FFlow AST.
        
        Args:
            text: Ren'Py script text
            
        Returns:
            FFlow AST
        """
        return self._parser.parse(text)
