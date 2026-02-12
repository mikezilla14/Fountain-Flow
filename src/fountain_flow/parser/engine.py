"""
Generic parser engine for fountain-flow.

This module provides a language-agnostic parser that works with any LanguageDefinition.
It uses the patterns and transformations defined in language modules to parse text into AST.
"""

import re
from typing import List, Optional, Dict, Any
from ..core.ast_nodes import (
    ScriptNode, ScriptAST, FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)
from ..languages.base import LanguageDefinition


class GenericParser:
    """
    Language-agnostic parser that uses a LanguageDefinition.
    
    This parser can handle any format for which there is a language definition,
    making it easy to add new formats without modifying the core parsing logic.
    """
    
    def __init__(self, language: LanguageDefinition):
        """
        Initialize the parser with a language definition.
        
        Args:
            language: The language definition to use for parsing
        """
        self.language = language
        self.nodes: ScriptAST = []
        self.in_frontmatter = False
        self.current_frontmatter: Dict[str, Any] = {}
        self.current_frontmatter_parent: Optional[str] = None
    
    def parse(self, script_text: str) -> ScriptAST:
        """
        Parse script text into an AST.
        
        Args:
            script_text: The script text to parse
            
        Returns:
            Abstract Syntax Tree as a list of ScriptNode objects
        """
        self.nodes = []
        self.in_frontmatter = False
        self.current_frontmatter = {}
        self.current_frontmatter_parent = None
        
        lines = script_text.split('\n')
        idx = 0
        
        while idx < len(lines):
            raw_line = lines[idx]
            
            # Calculate indentation
            match_indent = re.match(r'^(\s*)', raw_line)
            indent_chars = len(match_indent.group(1)) if match_indent else 0
            indent_level = indent_chars // 4
            
            line = raw_line.strip()
            
            # Skip empty lines
            if not line:
                idx += 1
                continue
            
            # Try to match against all patterns
            matched = False
            
            # Special handling for frontmatter (FFlow specific)
            if self.language.name == "fflow":
                matched, new_idx = self._handle_fflow_frontmatter(line, idx, indent_level)
                if matched:
                    idx = new_idx + 1  # Increment idx to move to next line
                    continue
            
            # Try all patterns in priority order
            for pattern in self.language.patterns:
                match = pattern.match(line)
                if not match:
                    continue
                
                # Handle the match based on pattern name and node type
                node = self._create_node_from_pattern(pattern, match, line, lines, idx, indent_level)
                
                if node is not None:
                    # Check if this is a character line (potential dialogue)
                    if isinstance(node, DialogueNode) and pattern.name == "character":
                        # Look ahead for dialogue text
                        dialogue_node, new_idx = self._parse_dialogue(lines, idx, line, indent_level)
                        if dialogue_node:
                            self.nodes.append(dialogue_node)
                            idx = new_idx
                            matched = True
                            break
                    else:
                        self.nodes.append(node)
                        matched = True
                        break
            
            if not matched:
                # Fallback: treat as action
                self.nodes.append(ActionNode(text=line, depth=indent_level))
            
            idx += 1
        
        return self.nodes
    
    def _handle_fflow_frontmatter(self, line: str, idx: int, indent_level: int) -> tuple[bool, int]:
        """Handle FFlow-specific frontmatter parsing."""
        # Check for frontmatter end marker
        if line == '===' and self.in_frontmatter:
            self.in_frontmatter = False
            self.nodes.append(FrontmatterNode(variables=self.current_frontmatter, depth=indent_level))
            return True, idx
        
        # Check if line starts with $ or $$
        is_fm_line = (line.startswith('$') or line.startswith('$$')) and '===' not in line
        
        if is_fm_line:
            if not self.in_frontmatter and not self.nodes:
                self.in_frontmatter = True
            
            if self.in_frontmatter:
                # Parent object: $$ name
                if line.startswith('$$'):
                    parent_match = re.match(r'^\$\$\s*(\w+)', line)
                    if parent_match:
                        self.current_frontmatter_parent = parent_match.group(1)
                        self.current_frontmatter[self.current_frontmatter_parent] = {}
                        return True, idx
                
                # Variable: $ key: value
                if line.startswith('$'):
                    parts = line.lstrip('$').split(':', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip()
                        
                        # Strip quotes from string values for normalization
                        # Both "value" and 'value' should become value
                        if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                            val = val[1:-1]
                        
                        if self.current_frontmatter_parent:
                            if self.current_frontmatter_parent not in self.current_frontmatter:
                                self.current_frontmatter[self.current_frontmatter_parent] = {}
                            self.current_frontmatter[self.current_frontmatter_parent][key] = val
                        else:
                            self.current_frontmatter[key] = val
                        return True, idx
        
        return False, idx
    
    def _create_node_from_pattern(self, pattern, match, line: str, lines: List[str], 
                                   idx: int, indent_level: int) -> Optional[ScriptNode]:
        """
        Create an AST node from a pattern match.
        
        Args:
            pattern: The PatternDef that matched
            match: The regex match object
            line: The current line
            lines: All lines being parsed
            idx: Current line index
            indent_level: Indentation level
            
        Returns:
            A ScriptNode or None
        """
        node_type = pattern.node_type
        
        if node_type is None:
            return None
        
        # Create node based on type
        if node_type == AssetNode:
            if pattern.name == "asset":
                return AssetNode(asset_type=match.group(1), data=match.group(2), depth=indent_level)
            elif pattern.name == "macro_bg":
                return AssetNode(asset_type="BG", data=match.group(1), depth=indent_level)
            elif pattern.name == "macro_show":
                return AssetNode(asset_type="SHOW", data=match.group(1), depth=indent_level)
            elif pattern.name == "macro_audio":
                return AssetNode(asset_type="MUSIC", data=match.group(1), depth=indent_level)
            elif pattern.name == "scene":
                return AssetNode(asset_type="BG", data=match.group(1), depth=indent_level)
            elif pattern.name == "show":
                return AssetNode(asset_type="SHOW", data=match.group(1), depth=indent_level)
        
        elif node_type == StateChangeNode:
            if pattern.name == "state_change":
                expr = match.group(1)
                # Normalize FFlow expressions to remove $ prefixes
                if hasattr(self.language, 'normalize_expression'):
                    expr = self.language.normalize_expression(expr)
                return StateChangeNode(expression=expr, depth=indent_level)
            elif pattern.name == "macro_set":
                # Twee format: <<set $var = val>>
                # Keep $ prefixes as-is since FFlow supports both formats
                var = match.group(1)  # Already stripped by pattern
                op = match.group(2)
                val = match.group(3)
                if op == 'to':
                    op = '='
                # Preserve $ prefixes in value expressions for FFlow
                expr = f"${var} {op} {val}"
                return StateChangeNode(expression=expr, depth=indent_level)
            elif pattern.name == "var_assign":
                # RenPy format: $ var = val
                var = match.group(1)
                val = match.group(2)
                expr = f"{var} = {val}"
                return StateChangeNode(expression=expr, depth=indent_level)
        
        elif node_type == DecisionNode:
            if pattern.name == "decision":
                return DecisionNode(text=match.group(1), depth=indent_level)
            elif pattern.name == "menu":
                return DecisionNode(text="Choice", depth=indent_level)
        
        elif node_type == ChoiceNode:
            if pattern.name == "choice_bracket":
                # Matches: + [Label] Description -> #Target
                label = match.group(1).strip()
                text = match.group(2).strip()
                target = match.group(3).strip()
                return ChoiceNode(label=label, text=text, target=target, depth=indent_level)
            elif pattern.name == "choice":
                # Matches: + ->Label->#Target (simplified)
                label = match.group(1).strip()
                target = match.group(2).strip()
                return ChoiceNode(label=label, text="", target=target, depth=indent_level)
            elif pattern.name == "implicit_choice":
                # Matches: ->Label->#Target
                text = match.group(1)
                target = match.group(2)
                # Set text="" to match Twee behavior and consistency with other choices
                return ChoiceNode(label=text, text="", target=target, depth=indent_level)
            elif pattern.name == "inline_choice":
                # Matches: [Label|#Target]
                # Target group captures name AFTER #
                label = match.group(1)
                target = match.group(2)
                return ChoiceNode(label=label, text="", target=target, depth=indent_level)
            elif pattern.name == "link":
                # Twee [[Label|Target]] link
                label = match.group(1)
                target = match.group(2) if match.lastindex >= 2 else label
                # Check if this is a "Continue" link (jump) vs a choice
                if label.strip().lower() == "continue":
                    # This is a jump converted to a link - convert back to JumpNode
                    return JumpNode(target=target, depth=indent_level)
                else:
                    # Regular choice link
                    return ChoiceNode(label=label, text="", target=target, depth=indent_level)
        
        elif node_type == JumpNode:
            if pattern.name == "jump":
                return JumpNode(target=match.group(1), depth=indent_level)
            elif pattern.name == "macro_goto":
                return JumpNode(target=match.group(1), depth=indent_level)
        
        elif node_type == LogicNode:
            if pattern.name in ["conditional_if", "macro_if", "if"]:
                cond = match.group(1) if match.lastindex >= 1 else None
                # Normalize FFlow conditions to remove $ prefixes
                if cond and hasattr(self.language, 'normalize_expression'):
                    cond = self.language.normalize_expression(cond)
                return LogicNode(start_condition=cond, depth=indent_level)
            elif pattern.name in ["conditional_elif", "macro_elseif"]:
                cond = match.group(1)
                # Normalize FFlow conditions to remove $ prefixes
                if hasattr(self.language, 'normalize_expression'):
                    cond = self.language.normalize_expression(cond)
                return LogicNode(start_condition=cond, is_elif=True, depth=indent_level)
            elif pattern.name in ["conditional_else", "macro_else", "else"]:
                return LogicNode(is_else=True, depth=indent_level)
            elif pattern.name in ["conditional_end", "macro_endif"]:
                return LogicNode(is_end=True, depth=indent_level)
        
        elif node_type == SceneHeadingNode:
            if pattern.name == "scene_heading":
                return SceneHeadingNode(scene_id="SCENE", text=line, depth=indent_level)
        
        elif node_type == SectionHeadingNode:
            if pattern.name == "section_heading":
                return SectionHeadingNode(text=line, anchor=match.group(1), depth=indent_level)
            elif pattern.name == "label":
                label = match.group(1)
                return SectionHeadingNode(text=label, anchor=label, depth=indent_level)
            elif pattern.name == "passage":
                # Twee passage: :: PassageName
                passage_name = match.group(1)
                return SectionHeadingNode(text=passage_name, anchor=passage_name, depth=indent_level)
        
        elif node_type == DialogueNode:
            if pattern.name == "dialogue":
                # Could be Twee format: **Character**: Text
                # or RenPy format: character "text"
                if self.language.name == "twee":
                    char = match.group(1)
                    text = match.group(2)
                    return DialogueNode(character=char, text=text, depth=indent_level)
                elif self.language.name == "renpy":
                    char = match.group(1)
                    text = match.group(2)
                    return DialogueNode(character=char, text=text, depth=indent_level)
            # For FFlow character pattern, return a marker (will be handled separately)
            return DialogueNode(character="", text="", depth=indent_level)
        
        return None
    
    def _parse_dialogue(self, lines: List[str], idx: int, character_line: str, 
                       indent_level: int) -> tuple[Optional[DialogueNode], int]:
        """
        Parse dialogue block (FFlow format).
        
        Args:
            lines: All lines
            idx: Current line index (character line)
            character_line: The character name line
            indent_level: Indentation level
            
        Returns:
            Tuple of (DialogueNode or None, new index)
        """
        if idx + 1 >= len(lines) or not lines[idx + 1].strip():
            return None, idx
        
        character_name = character_line
        parenthetical = None
        dialogue_text = ""
        next_line_idx = idx + 1
        next_line = lines[next_line_idx].strip()
        
        # Check for parenthetical
        p_match = re.match(r'^\s*(\(.*\))\s*$', next_line)
        if p_match:
            parenthetical = p_match.group(1)
            next_line_idx += 1
            if next_line_idx < len(lines):
                next_line = lines[next_line_idx].strip()
        
        # Collect dialogue lines
        dialogue_lines = []
        while next_line_idx < len(lines):
            d_line = lines[next_line_idx].strip()
            if not d_line:
                break
            
            # Check if we hit another structure element
            should_break = False
            for pattern in self.language.patterns:
                if pattern.name in ["section_heading", "asset", "state_change", "choice"]:
                    if pattern.match(d_line):
                        should_break = True
                        break
            
            if should_break:
                break
            
            dialogue_lines.append(d_line)
            next_line_idx += 1
        
        dialogue_text = " ".join(dialogue_lines)
        
        return DialogueNode(
            character=character_name,
            text=dialogue_text,
            parenthetical=parenthetical,
            depth=indent_level
        ), next_line_idx
