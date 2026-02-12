"""
FFlow (Fountain-Flow) language definition.

This module defines the syntax rules and transformation logic for the FFlow format,
which is the base format for fountain-flow. It extends standard Fountain screenplay
format with interactive narrative elements.
"""

from typing import Dict, Any
from .base import LanguageDefinition, PatternDef
from ..core.ast_nodes import (
    FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)


class FFlowLanguage(LanguageDefinition):
    """FFlow language definition."""
    
    @property
    def name(self) -> str:
        return "fflow"
    
    @property
    def file_extensions(self) -> list:
        return [".fflow"]
    
    def _initialize_patterns(self):
        """Initialize FFlow syntax patterns based on the specification."""
        
        # Frontmatter patterns (highest priority)
        self.patterns.append(PatternDef(
            name="frontmatter_end",
            regex=r'^===\s*$',
            priority=100
        ))
        
        self.patterns.append(PatternDef(
            name="frontmatter_parent",
            regex=r'^\$\$\s*(\w+)',
            priority=95
        ))
        
        self.patterns.append(PatternDef(
            name="frontmatter_var",
            regex=r'^\$\s*(.+)',
            priority=90
        ))
        
        # Flow control patterns
        self.patterns.append(PatternDef(
            name="asset",
            regex=r'^\s*!\s*(\w+):\s*(.+)',
            node_type=AssetNode,
            priority=80
        ))
        
        self.patterns.append(PatternDef(
            name="state_change",
            regex=r'^\s*~\s*(.+)',
            node_type=StateChangeNode,
            priority=75
        ))
        
        self.patterns.append(PatternDef(
            name="decision",
            regex=r'^\s*\?\s*(.+)',
            node_type=DecisionNode,
            priority=70
        ))
        
        # Choice with brackets: + [Label] Description -> #Target
        self.patterns.append(PatternDef(
            name="choice_bracket",
            regex=r'^\s*\+\s*\[(.+?)\]\s*(.*?)\s*->\s*#(.+)$',
            node_type=ChoiceNode,
            priority=66
        ))
        
        # Choice without brackets: + ->Label->#Target (simplified)
        self.patterns.append(PatternDef(
            name="choice",
            regex=r'^\s*\+\s*->(.+?)->\s*#(.+)$',
            node_type=ChoiceNode,
            priority=65
        ))
        
        self.patterns.append(PatternDef(
            name="jump",
            regex=r'^\s*->\s*#(.+)',
            node_type=JumpNode,
            priority=60
        ))
        
        # Inline choice with bracket syntax: [Label|#Target]
        # Must have # in target part
        self.patterns.append(PatternDef(
            name="inline_choice",
            regex=r'^\s*\[(.*?)\|#(.+?)\]\s*$',
            node_type=ChoiceNode,
            priority=58
        ))
        
        self.patterns.append(PatternDef(
            name="implicit_choice",
            regex=r'^\s*->\s*(?!#)(.+?)->\s*#(.+)$',
            node_type=ChoiceNode,
            priority=55
        ))
        
        # Conditional patterns
        self.patterns.append(PatternDef(
            name="conditional_if",
            regex=r'^\s*\(IF:\s*(.+)\)',
            node_type=LogicNode,
            priority=50
        ))
        
        self.patterns.append(PatternDef(
            name="conditional_elif",
            regex=r'^\s*\(ELIF:\s*(.+)\)',
            node_type=LogicNode,
            priority=50
        ))
        
        self.patterns.append(PatternDef(
            name="conditional_else",
            regex=r'^\s*\(ELSE\)',
            node_type=LogicNode,
            priority=50
        ))
        
        self.patterns.append(PatternDef(
            name="conditional_end",
            regex=r'^\s*\(END\)',
            node_type=LogicNode,
            priority=50
        ))
        
        # Structural patterns
        self.patterns.append(PatternDef(
            name="section_heading",
            regex=r'^\s*#\s*(.+)',
            node_type=SectionHeadingNode,
            priority=45
        ))
        
        self.patterns.append(PatternDef(
            name="scene_heading",
            regex=r'^(INT\.|EXT\.|EST\.|INT\./EXT\.|I/E)\s*(.+)',
            node_type=SceneHeadingNode,
            priority=40
        ))
        
        # Character name (for dialogue detection)
        self.patterns.append(PatternDef(
            name="character",
            regex=r'^([A-Z0-9 ]*[A-Z0-9]+)(\s*\(.*\))?$',
            node_type=DialogueNode,
            priority=30
        ))
        
        # Parenthetical
        self.patterns.append(PatternDef(
            name="parenthetical",
            regex=r'^\s*(\(.*\))\s*$',
            priority=35
        ))
    
    # FFlow uses identity transformations (no prefix changes)
    
    def normalize_expression(self, expr: str) -> str:
        """Strip $ prefixes from expressions for consistent FFlow syntax."""
        import re
        # Remove $ prefix from all variable references
        # Matches $varname, $object.property, $_localvar
        return re.sub(r'\$([a-zA-Z_][\w.]*)', r'\1', expr)
    
    def transform_variable_reference(self, var_name: str) -> str:
        """FFlow variables don't have prefixes."""
        return var_name
    
    def transform_expression(self, expr: str) -> str:
        """FFlow expressions are unchanged."""
        return expr
    
    def transform_condition(self, cond: str) -> str:
        """FFlow conditions are unchanged."""
        return cond
    
    # Output formatting methods
    
    def format_frontmatter(self, variables: Dict[str, Any]) -> str:
        """Format frontmatter in FFlow syntax."""
        lines = []
        for key, value in variables.items():
            if isinstance(value, dict):
                # Parent object
                lines.append(f"$$ {key}")
                for child_key, child_val in value.items():
                    lines.append(f"    $ {child_key}: {child_val}")
            else:
                # Simple variable
                lines.append(f"$ {key}: {value}")
        lines.append("===")
        return "\n".join(lines)
    
    def format_scene_heading(self, scene_id: str, text: str) -> str:
        """Format a scene heading."""
        return text
    
    def format_section_heading(self, anchor: str, text: str) -> str:
        """Format a section heading."""
        return f"# {anchor}"
    
    def format_action(self, text: str) -> str:
        """Format an action line."""
        return text
    
    def format_dialogue(self, character: str, text: str, parenthetical: str = None) -> str:
        """Format dialogue."""
        if parenthetical:
            return f"{character}\n{parenthetical}\n{text}"
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
        # Simplified syntax: + ->Label->#Target
        # Note: We prioritize the simplified link syntax over separate description text
        if target:
            return f"+ ->{label}->#{target}"
        return f"+ ->{label}->#"
    
    def format_jump(self, target: str) -> str:
        """Format a jump."""
        return f"-> #{target}"
