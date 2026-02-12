"""
Generic transpiler engine for fountain-flow.

This module provides a language-agnostic transpiler that uses LanguageDefinitions
to convert AST nodes into any target format.
"""

from typing import List, Optional
from ..core.ast_nodes import (
    ScriptNode, ScriptAST, FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)
from ..languages.base import LanguageDefinition


class GenericTranspiler:
    """
    Language-agnostic transpiler.
    
    Uses a target LanguageDefinition to format AST nodes into the target language's syntax.
    """
    
    def __init__(self, target_language: LanguageDefinition):
        """
        Initialize the transpiler.
        
        Args:
            target_language: The language definition for the output format
        """
        self.language = target_language
        self.indent_level = 0
        self.last_was_section = False
    
    def transpile(self, ast: ScriptAST) -> str:
        """
        Transpile an AST to text in the target language.
        
        Args:
            ast: The Abstract Syntax Tree to transpile
            
        Returns:
            Formatted text in the target language
        """
        output_lines = []
        
        for node in ast:
            result = self.visit(node)
            if result:
                output_lines.append(result)
        
        return "\n".join(output_lines)
    
    def visit(self, node: ScriptNode) -> Optional[str]:
        """
        Visit a node and format it using the language definition.
        
        Args:
            node: The node to visit
            
        Returns:
            Formatted text for this node
        """
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node: ScriptNode) -> str:
        """Fallback visit method."""
        return str(node)
    
    def indent(self, text: str) -> str:
        """Add indentation to text."""
        return ("    " * self.indent_level) + text
    
    def visit_FrontmatterNode(self, node: FrontmatterNode) -> str:
        """Visit a frontmatter node."""
        return self.language.format_frontmatter(node.variables)
    
    def visit_SceneHeadingNode(self, node: SceneHeadingNode) -> str:
        """Visit a scene heading node."""
        self.last_was_section = True
        result = self.language.format_scene_heading(node.scene_id, node.text)
        return result
    
    def visit_SectionHeadingNode(self, node: SectionHeadingNode) -> str:
        """Visit a section heading node."""
        self.last_was_section = True
        return self.language.format_section_heading(node.anchor, node.text)
    
    def visit_ActionNode(self, node: ActionNode) -> str:
        """Visit an action node."""
        result = self.language.format_action(node.text)
        if self.indent_level > 0 and self.language.name == "renpy":
            result = self.indent(result)
        self.last_was_section = False
        return result
    
    def visit_DialogueNode(self, node: DialogueNode) -> str:
        """Visit a dialogue node."""
        result = self.language.format_dialogue(node.character, node.text, node.parenthetical)
        if self.indent_level > 0 and self.language.name == "renpy":
            result = self.indent(result)
        self.last_was_section = False
        return result
    
    def visit_AssetNode(self, node: AssetNode) -> str:
        """Visit an asset node."""
        result = self.language.format_asset(node.asset_type, node.data)
        if self.indent_level > 0 and self.language.name == "renpy":
            result = self.indent(result)
        return result
    
    def visit_StateChangeNode(self, node: StateChangeNode) -> str:
        """Visit a state change node."""
        result = self.language.format_state_change(node.expression)
        if self.indent_level > 0 and self.language.name == "renpy":
            result = self.indent(result)
        return result
    
    def visit_LogicNode(self, node: LogicNode) -> str:
        """Visit a logic node."""
        # Handle indentation for indentation-based languages
        if node.is_end:
            if self.language.name == "renpy":
                # RenPy uses indentation, so just decrease level
                if self.indent_level > 0:
                    self.indent_level -= 1
                return ""  # No explicit end marker
            else:
                # Other languages use explicit end markers
                return self.language.format_logic_end()
        
        result = ""
        if node.is_else:
            if self.language.name == "renpy" and self.indent_level > 0:
                self.indent_level -= 1
            result = self.language.format_logic_else()
            if self.language.name == "renpy":
                result = self.indent(result)
                self.indent_level += 1
        elif node.is_elif:
            if self.language.name == "renpy" and self.indent_level > 0:
                self.indent_level -= 1
            result = self.language.format_logic_elif(node.start_condition)
            if self.language.name == "renpy":
                result = self.indent(result)
                self.indent_level += 1
        else:
            # IF statement
            result = self.language.format_logic_start(node.start_condition)
            if self.language.name == "renpy":
                result = self.indent(result)
                self.indent_level += 1
        
        return result
    
    def visit_DecisionNode(self, node: DecisionNode) -> str:
        """Visit a decision node."""
        result = self.language.format_decision(node.text)
        if self.language.name == "renpy":
            result = self.indent(result)
            self.indent_level += 1
        return result
    
    def visit_ChoiceNode(self, node: ChoiceNode) -> str:
        """Visit a choice node."""
        result = self.language.format_choice(node.label, node.text, node.target)
        if self.indent_level > 0 and self.language.name == "renpy":
            result = self.indent(result)
        return result
    
    def visit_JumpNode(self, node: JumpNode) -> str:
        """Visit a jump node."""
        result = self.language.format_jump(node.target)
        if self.indent_level > 0 and self.language.name == "renpy":
            result = self.indent(result)
        return result
