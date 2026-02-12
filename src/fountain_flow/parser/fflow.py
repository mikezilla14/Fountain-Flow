"""
FFlow parser - Parses Fountain-Flow format into AST.

This module provides backward-compatible interfaces while using the new
language-based parser architecture under the hood.
"""

import re
from typing import List, Optional, Dict, Any
from ..core.ast_nodes import (
    ScriptNode, ScriptAST, FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)
from .engine import GenericParser
from ..languages.fflow import FFlowLanguage


class FFlowParser:
    """
    Fountain-Flow parser.
    
    This class provides backward compatibility while using the new language-based
    parser architecture. It's a thin wrapper around GenericParser with FFlowLanguage.
    """
    
    # Legacy regex patterns - kept for reference but not used
    REGEX_ASSET = r'^\s*!\s*(\w+):\s*(.+)'
    REGEX_STATE = r'^\s*~\s*(.+)'
    REGEX_DECISION = r'^\s*\?\s*(.+)'
    REGEX_CHOICE = r'^\s*\+\s*\[(.*?)\]\s*(.*?)\s*(?:->\s*#(.+))?$' 
    REGEX_CONDITIONAL = r'^\s*\(IF:\s*(.+)\)'
    REGEX_ELSE = r'^\s*\(ELSE\)'
    REGEX_END = r'^\s*\(END\)'
    REGEX_JUMP = r'^\s*->\s*#(.+)'
    REGEX_SECTION = r'^\s*#\s*(.+)'
    REGEX_SCENE = r'^(INT\.|EXT\.|EST\.|INT\./EXT\.|I/E)\s*(.+)'
    REGEX_CHARACTER = r'^([A-Z0-9 ]*[A-Z0-9]+)(\s*\(.*\))?$'
    REGEX_PARENTHETICAL = r'^\s*(\(.*\))\s*$'
    REGEX_OBJECT_PARENT = r'^\$\$\s*(\w+)'
    REGEX_IMPLICIT_CHOICE = r'^(.+?)\s*->\s*#(.+)$'

    def __init__(self):
        self.nodes: ScriptAST = []
        self.in_frontmatter = False
        self.current_frontmatter = {}
        self.current_frontmatter_parent = None
        
        # Initialize the generic parser with FFlow language
        self._parser = GenericParser(FFlowLanguage())

    def parse(self, script_text: str) -> ScriptAST:
        """
        Parse FFlow script text into an AST.
        
        Args:
            script_text: The FFlow script text
            
        Returns:
            Abstract Syntax Tree
        """
        return self._parser.parse(script_text)


def parse(script_text: str) -> ScriptAST:
    """
    Convenience function to parse FFlow script.
    
    Args:
        script_text: The FFlow script text
        
    Returns:
        Abstract Syntax Tree
    """
    parser = FFlowParser()
    return parser.parse(script_text)
