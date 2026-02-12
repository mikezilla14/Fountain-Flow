"""
Transpilers - Convert FFlow AST to various output formats.

This module provides transpilers for Twee, Ren'Py, and FFlow formats using
the new language-based architecture for consistency and maintainability.
"""

from abc import ABC, abstractmethod
import re
from typing import List, Dict, Any
from ..core.ast_nodes import (
    ScriptNode, ScriptAST, FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)
from .engine import GenericTranspiler
from ..languages.fflow import FFlowLanguage
from ..languages.twee import TweeLanguage
from ..languages.renpy import RenPyLanguage


class BaseTranspiler(ABC):
    """Base class for transpilers (for backward compatibility)."""
    
    @abstractmethod
    def transpile(self, ast: ScriptAST) -> str:
        pass
    
    def visit(self, node: ScriptNode) -> str:
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ScriptNode) -> str:
        return str(node)


class TweeTranspiler(BaseTranspiler):
    """
    Transpiles FFlow AST to Twine (SugarCube format).
    
    Wrapper around GenericTranspiler with TweeLanguage for backward compatibility.
    """
    
    def __init__(self):
        self.last_was_section = False
        self._transpiler = GenericTranspiler(TweeLanguage())
    
    def transpile(self, ast: ScriptAST) -> str:
        """
        Transpile FFlow AST to Twee format.
        
        Args:
            ast: The FFlow AST
            
        Returns:
            Twee/SugarCube formatted text
        """
        return self._transpiler.transpile(ast)
    
    # Keep old methods for any direct usage (though they won't be called)
    def _convert_expression(self, expr: str) -> str:
        """Legacy method - kept for compatibility."""
        return self._transpiler.language.transform_expression(expr)
    
    def _ensure_vars(self, cond: str) -> str:
        """Legacy method - kept for compatibility."""
        return self._transpiler.language.transform_condition(cond)


class RenPyTranspiler(BaseTranspiler):
    """
    Transpiles FFlow AST to Ren'Py script.
    
    Wrapper around GenericTranspiler with RenPyLanguage for backward compatibility.
    """
    
    def __init__(self):
        self.indent_level = 0
        self._transpiler = GenericTranspiler(RenPyLanguage())
    
    def transpile(self, ast: ScriptAST) -> str:
        """
        Transpile FFlow AST to Ren'Py format.
        
        Args:
            ast: The FFlow AST
            
        Returns:
            Ren'Py script text
        """
        return self._transpiler.transpile(ast)
    
    def indent(self, s: str) -> str:
        """Legacy method - kept for compatibility."""
        return self._transpiler.indent(s)


class FFlowTranspiler(BaseTranspiler):
    """
    Transpiles any AST back to FFlow format.
    
    Useful for roundtrip conversion and normalization.
    """
    
    def __init__(self):
        self._transpiler = GenericTranspiler(FFlowLanguage())
    
    def transpile(self, ast: ScriptAST) -> str:
        """
        Transpile AST to FFlow format.
        
        Args:
            ast: The AST to transpile
            
        Returns:
            FFlow formatted text
        """
        return self._transpiler.transpile(ast)
