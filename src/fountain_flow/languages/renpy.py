"""
Ren'Py language definition.

This module defines the syntax rules and transformation logic for Ren'Py script format,
commonly used for visual novels.
"""

from typing import Dict, Any
from .base import LanguageDefinition, PatternDef
from ..core.ast_nodes import (
    FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)


class RenPyLanguage(LanguageDefinition):
    """Ren'Py language definition."""
    
    @property
    def name(self) -> str:
        return "renpy"
    
    @property
    def file_extensions(self) -> list:
        return [".rpy"]
    
    def _initialize_patterns(self):
        """Initialize Ren'Py syntax patterns."""
        
        # Label (section/scene markers)
        self.patterns.append(PatternDef(
            name="label",
            regex=r'^label\s+(\w+):',
            node_type=SectionHeadingNode,
            priority=90
        ))
        
        # Variable assignment
        self.patterns.append(PatternDef(
            name="var_assign",
            regex=r'^\$\s*(\w+)\s*=\s*(.+)',
            node_type=StateChangeNode,
            priority=85
        ))
        
        # Scene command (background)
        self.patterns.append(PatternDef(
            name="scene",
            regex=r'^scene\s+(.+)',
            node_type=AssetNode,
            priority=80
        ))
        
        # Show command (character sprite)
        self.patterns.append(PatternDef(
            name="show",
            regex=r'^show\s+(.+)',
            node_type=AssetNode,
            priority=80
        ))
        
        # Menu (decision point)
        self.patterns.append(PatternDef(
            name="menu",
            regex=r'^menu:',
            node_type=DecisionNode,
            priority=75
        ))
        
        # Jump command
        self.patterns.append(PatternDef(
            name="jump",
            regex=r'^jump\s+(\w+)',
            node_type=JumpNode,
            priority=70
        ))
        
        # Conditionals
        self.patterns.append(PatternDef(
            name="if",
            regex=r'^if\s+(.+):',
            node_type=LogicNode,
            priority=65
        ))
        
        self.patterns.append(PatternDef(
            name="else",
            regex=r'^else:',
            node_type=LogicNode,
            priority=65
        ))
        
        # Dialogue with character
        self.patterns.append(PatternDef(
            name="dialogue",
            regex=r'^(\w+)\s+"(.+)"',
            node_type=DialogueNode,
            priority=60
        ))
        
        # Action (quoted text)
        self.patterns.append(PatternDef(
            name="action",
            regex=r'^"(.+)"',
            node_type=ActionNode,
            priority=55
        ))
    
    # Expression transformations (RenPy uses Python syntax)
    
    def transform_variable_reference(self, var_name: str) -> str:
        """RenPy variables don't need prefixes in expressions."""
        return var_name
    
    def transform_expression(self, expr: str) -> str:
        """RenPy expressions use Python syntax."""
        return expr
    
    def transform_condition(self, cond: str) -> str:
        """RenPy conditions use Python syntax."""
        return cond
    
    # Output formatting methods
    
    def format_frontmatter(self, variables: Dict[str, Any]) -> str:
        """Format frontmatter as variable definitions."""
        lines = []
        for key, value in variables.items():
            if isinstance(value, dict):
                # Python dict literal
                dict_str = ", ".join([f'"{k}": {v}' for k, v in value.items()])
                lines.append(f"$ {key} = {{ {dict_str} }}")
            else:
                lines.append(f"$ {key} = {value}")
        return "\n".join(lines)
    
    def format_scene_heading(self, scene_id: str, text: str) -> str:
        """Format as label."""
        safe_id = text.replace(" ", "_").replace(".", "_").replace("-", "_").lower()
        return f"label {safe_id}:"
    
    def format_section_heading(self, anchor: str, text: str) -> str:
        """Format as label."""
        safe_id = anchor.replace(" ", "_").lower()
        return f"label {safe_id}:"
    
    def format_action(self, text: str) -> str:
        """Format action as quoted text."""
        return f'"{text}"'
    
    def format_dialogue(self, character: str, text: str, parenthetical: str = None) -> str:
        """Format dialogue."""
        # RenPy format: char "text"
        if parenthetical:
            # Could include parenthetical in text or ignore
            return f'{character.lower()} "{text}"'
        return f'{character.lower()} "{text}"'
    
    def format_asset(self, asset_type: str, data: str) -> str:
        """Format asset directive."""
        if asset_type.upper() == "BG":
            return f"scene {data}"
        elif asset_type.upper() == "SHOW":
            return f"show {data}"
        elif asset_type.upper() in ["MUSIC", "SFX"]:
            return f'play music "{data}"'
        else:
            return f"# Asset: {asset_type}: {data}"
    
    def format_state_change(self, expression: str) -> str:
        """Format state change."""
        return f"$ {expression}"
    
    def format_logic_start(self, condition: str) -> str:
        """Format IF."""
        return f"if {condition}:"
    
    def format_logic_elif(self, condition: str) -> str:
        """Format ELIF."""
        return f"elif {condition}:"
    
    def format_logic_else(self) -> str:
        """Format ELSE."""
        return "else:"
    
    def format_logic_end(self) -> str:
        """RenPy doesn't use explicit end markers (uses indentation)."""
        return ""  # Empty string, handled by indentation
    
    def format_decision(self, text: str) -> str:
        """Format decision as menu."""
        return "menu:"
    
    def format_choice(self, label: str, text: str, target: str) -> str:
        """Format choice as menu item."""
        return f'    "{label}":'
    
    def format_jump(self, target: str) -> str:
        """Format jump."""
        safe_target = target.replace(" ", "_").lower()
        return f"jump {safe_target}"
