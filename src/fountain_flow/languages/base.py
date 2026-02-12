"""
Language definition base class for fountain-flow parsers and transpilers.

This module defines the abstract interface that all language definitions must implement.
Language definitions encapsulate all language-specific syntax rules, patterns, and
transformation logic, allowing the core parser and transpiler to be language-agnostic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Pattern, Callable, Type, Any, Optional
import re
import sys
from ..core.ast_nodes import ScriptNode


@dataclass
class PatternDef:
    """Definition of a syntax pattern for a language element."""
    name: str
    regex: str
    compiled: Optional[Pattern] = field(default=None, init=False)
    node_type: Optional[Type[ScriptNode]] = None
    priority: int = 0  # Higher priority patterns are checked first
    
    def __post_init__(self):
        """Compile the regex pattern after initialization."""
        self.compiled = re.compile(self.regex)
    
    def match(self, line: str):
        """Match the pattern against a line of text."""
        return self.compiled.match(line)


class LanguageDefinition(ABC):
    """
    Abstract base class for language definitions.
    
    Each language definition encapsulates:
    1. Syntax patterns (regex) for all language elements
    2. Node type mappings (which AST node to create)
    3. Expression transformers (how to convert expressions between formats)
    4. Formatting rules (how to generate output text)
    """
    
    def __init__(self):
        self.patterns: List[PatternDef] = []
        self._pattern_map: Dict[str, PatternDef] = {}
        self._initialize_patterns()
        # Sort patterns by priority (higher first)
        self.patterns.sort(key=lambda p: p.priority, reverse=True)
        self._pattern_map = {p.name: p for p in self.patterns}
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Language name (e.g., 'fflow', 'twee', 'renpy')."""
        pass
    
    @property
    @abstractmethod
    def file_extensions(self) -> List[str]:
        """File extensions for this language (e.g., ['.fflow'])."""
        pass
    
    @abstractmethod
    def _initialize_patterns(self):
        """Initialize the syntax patterns for this language."""
        pass
    
    def get_pattern(self, name: str) -> Optional[PatternDef]:
        """Get a pattern by name."""
        return self._pattern_map.get(name)
    
    # Expression transformation methods
    
    def transform_variable_reference(self, var_name: str) -> str:
        """
        Transform a variable reference for this language.
        E.g., 'HP' -> '$HP' for Twee, 'HP' -> 'HP' for FFlow
        """
        return var_name
    
    def transform_expression(self, expr: str) -> str:
        """
        Transform a complete expression for this language.
        E.g., 'HP += 5' -> '$HP += 5' for Twee
        """
        return expr
    
    def transform_condition(self, cond: str) -> str:
        """
        Transform a conditional expression for this language.
        E.g., 'HP > 0' -> '$HP > 0' for Twee
        """
        return cond
    
    # Output formatting methods (for transpilers)
    
    def format_frontmatter(self, variables: Dict[str, Any]) -> str:
        """Format frontmatter/initialization block."""
        return ""
    
    def format_scene_heading(self, scene_id: str, text: str) -> str:
        """Format a scene heading."""
        return text
    
    def format_section_heading(self, anchor: str, text: str) -> str:
        """Format a section heading."""
        return text
    
    def format_action(self, text: str) -> str:
        """Format an action line."""
        return text
    
    def format_dialogue(self, character: str, text: str, parenthetical: Optional[str] = None) -> str:
        """Format dialogue."""
        return f"{character}\n{text}"
    
    def format_asset(self, asset_type: str, data: str) -> str:
        """Format an asset directive."""
        return f"! {asset_type}: {data}"
    
    def format_state_change(self, expression: str) -> str:
        """Format a state change."""
        return f"~ {expression}"
    
    def format_logic_start(self, condition: str) -> str:
        """Format the start of a conditional block."""
        return f"(IF: {condition})"
    
    def format_logic_elif(self, condition: str) -> str:
        """Format an elif in a conditional block."""
        return f"(ELIF: {condition})"
    
    def format_logic_else(self) -> str:
        """Format an else in a conditional block."""
        return "(ELSE)"
    
    def format_logic_end(self) -> str:
        """Format the end of a conditional block."""
        return "(END)"
    
    def format_decision(self, text: str) -> str:
        """Format a decision prompt."""
        return f"? {text}"
    
    def format_choice(self, label: str, text: str, target: str) -> str:
        """Format a choice option."""
        if target:
            return f"+ [{label}] {text} -> #{target}"
        return f"+ [{label}] {text}"
    
    def format_jump(self, target: str) -> str:
        """Format a jump."""
        return f"-> #{target}"
