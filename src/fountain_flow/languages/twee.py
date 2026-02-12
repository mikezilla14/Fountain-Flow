"""
Twee (SugarCube) language definition.

This module defines the syntax rules and transformation logic for Twee format
with SugarCube macros, commonly used in Twine interactive fiction.
"""

import re
from typing import Dict, Any
from .base import LanguageDefinition, PatternDef
from ..core.ast_nodes import (
    FrontmatterNode, SceneHeadingNode, SectionHeadingNode,
    ActionNode, DialogueNode, AssetNode, StateChangeNode, LogicNode,
    DecisionNode, ChoiceNode, JumpNode
)


class TweeLanguage(LanguageDefinition):
    """Twee/SugarCube language definition."""
    
    @property
    def name(self) -> str:
        return "twee"
    
    @property
    def file_extensions(self) -> list:
        return [".twee", ".tw"]
    
    def _initialize_patterns(self):
        """Initialize Twee/SugarCube syntax patterns."""
        
        # Passage structure
        self.patterns.append(PatternDef(
            name="passage",
            regex=r'^::\s*(.+)',
            node_type=SectionHeadingNode,
            priority=100
        ))
        
        # Macros - State changes
        self.patterns.append(PatternDef(
            name="macro_set",
            regex=r'<<set\s+\$([\w.]+)\s*(to|=|\+=|-=|\*=|/=)\s*(.+)>>',
            node_type=StateChangeNode,
            priority=90
        ))
        
        # Macro patterns
        self.patterns.append(PatternDef(
            name="macro_if",
            regex=r'^\s*<<if\s+(.+?)>>\s*$',
            node_type=LogicNode,
            priority=80
        ))
        
        self.patterns.append(PatternDef(
            name="macro_elseif",
            regex=r'^\s*<<elseif\s+(.+?)>>\s*$',
            node_type=LogicNode,
            priority=80
        ))
        
        self.patterns.append(PatternDef(
            name="macro_else",
            regex=r'<<else>>',
            node_type=LogicNode,
            priority=80
        ))
        
        self.patterns.append(PatternDef(
            name="macro_endif",
            regex=r'<<(?:endif|/if)>>',
            node_type=LogicNode,
            priority=80
        ))
        
        # Macros - Navigation
        self.patterns.append(PatternDef(
            name="macro_goto",
            regex=r'<<goto\s+"(.+)">>',
            node_type=JumpNode,
            priority=80
        ))
        
        # Macros - Assets
        self.patterns.append(PatternDef(
            name="macro_bg",
            regex=r'<<bg\s+"(.+)">>',
            node_type=AssetNode,
            priority=75
        ))
        
        self.patterns.append(PatternDef(
            name="macro_show",
            regex=r'<<show\s+"(.+)">>',
            node_type=AssetNode,
            priority=75
        ))
        
        self.patterns.append(PatternDef(
            name="macro_audio",
            regex=r'<<audio\s+"(.+)"\s+play>>',
            node_type=AssetNode,
            priority=75
        ))
        
        self.patterns.append(PatternDef(
            name="macro_run",
            regex=r'<<run\s+(.+)>>',
            priority=70
        ))
        
        # Links (choices)
        self.patterns.append(PatternDef(
            name="link",
            regex=r'\[\[(.*?)(?:\|(.*?))?\]\]',
            node_type=ChoiceNode,
            priority=65
        ))
        
        # HTML image tags
        self.patterns.append(PatternDef(
            name="img_tag",
            regex=r'<img src="(.+)">',
            node_type=AssetNode,
            priority=60
        ))
        
        # Dialogue (bold text with colon)
        self.patterns.append(PatternDef(
            name="dialogue",
            regex=r'\*\*(.+?)\*\*:(.+)',
            node_type=DialogueNode,
            priority=50
        ))
    
    # Expression transformation methods
    
    def transform_variable_reference(self, var_name: str) -> str:
        """Add $ prefix for Twee variables."""
        if not var_name.startswith('$'):
            return f'${var_name}'
        return var_name
    
    def transform_expression(self, expr: str) -> str:
        """Transform expression to add $ prefixes to variables."""
        # This function needs to handle cases like:
        # "player.hp" -> "$player.hp"
        # "$player.hp" -> "$player.hp" (no change)
        # "player.hp > 5" -> "$player.hp > 5"
        # "$player.hp = $player.maxHP" -> "$player.hp = $player.maxHP" (no change)
        # "random(3, player.maxHP)" -> "random(3, $player.maxHP)" (don't prefix function names)
        
        # Use a simple state machine approach
        result = []
        i = 0
        while i < len(expr):
            ch = expr[i]
            
            # Check if we're at the start of an identifier
            if ch.isalpha() or ch == '_':
                # Look back to see if there's already a $
                has_dollar = (i > 0 and expr[i-1] == '$')
                
                # Collect the full identifier (including dots for paths like player.hp)
                j = i
                while j < len(expr) and (expr[j].isalnum() or expr[j] in '_.'):
                    j += 1
                
                identifier = expr[i:j]
                
                # Check if this is a function call (identifier followed by '(')
                # Skip whitespace after identifier to check
                k = j
                while k < len(expr) and expr[k].isspace():
                    k += 1
                is_function = (k < len(expr) and expr[k] == '(')
                
                # Add $ prefix if not already there and not a function call
                if not has_dollar and not is_function:
                    result.append('$')
                result.append(identifier)
                i = j
            else:
                result.append(ch)
                i += 1
        
        return ''.join(result)
    
    def transform_condition(self, cond: str) -> str:
        """Transform condition to add $ prefixes."""
        return self.transform_expression(cond)
    
    def strip_variable_prefix(self, expr: str) -> str:
        """Remove $ prefix from variables (for parsing Twee -> FFlow)."""
        return re.sub(r'\$([a-zA-Z_])', r'\1', expr)
    
    # Output formatting methods
    
    def format_frontmatter(self, variables: Dict[str, Any]) -> str:
        """Format frontmatter as StoryInit passage."""
        lines = [":: StoryInit"]
        for key, value in variables.items():
            if isinstance(value, dict):
                # Object literal - need to quote string values but not numbers
                obj_parts = []
                for k, v in value.items():
                    # Check if value is already a number or boolean
                    if isinstance(v, (int, float, bool)):
                        obj_parts.append(f"{k}: {v}")
                    else:
                        # String value - check if it's a numeric string
                        v_str = str(v)
                        # Try to detect if it's a number
                        try:
                            # Try parsing as int or float
                            num_val = float(v_str)
                            # Use int representation if it's a whole number
                            if num_val == int(num_val):
                                obj_parts.append(f"{k}: {int(num_val)}")
                            else:
                                obj_parts.append(f"{k}: {num_val}")
                        except ValueError:
                            # Not a number - quote it
                            if not (v_str.startswith('"') or v_str.startswith("'")):
                                v_str = f'"{v_str}"'
                            obj_parts.append(f"{k}: {v_str}")
                obj_str = ", ".join(obj_parts)
                lines.append(f"<<set ${key} to {{ {obj_str} }}>>")
            else:
                lines.append(f"<<set ${key} to {value}>>")
        lines.append("")  # Empty line after StoryInit
        return "\n".join(lines)
    
    def format_scene_heading(self, scene_id: str, text: str) -> str:
        """Format as a passage."""
        # Convert scene heading to safe passage name
        # Strip periods first, then replace spaces with underscores
        safe_id = text.replace(".", "").replace(" ", "_").replace("-", "_")
        return f":: {safe_id}"
    
    def format_section_heading(self, anchor: str, text: str) -> str:
        """Format as a passage."""
        safe_id = anchor.replace(" ", "_").replace(".", "_")
        return f":: {safe_id}"
    
    def format_action(self, text: str) -> str:
        """Format action text, handling inline jumps and variable interpolation."""
        import re
        
        # Check for inline jump pattern: "text -> #target"
        match = re.match(r'^(.+?)\s*->\s*#(.+)$', text)
        if match:
            action_text = match.group(1).strip()
            target = match.group(2).strip()
            safe_target = target.replace(" ", "_").replace(".", "_")
            # Apply variable interpolation to action text for Twee display
            action_text = self._add_variable_prefixes(action_text)
            return f"{action_text}\n<<goto \"{safe_target}\">>"
        
        # Apply variable interpolation for Twee display
        return self._add_variable_prefixes(text)
    
    def _add_variable_prefixes(self, text: str) -> str:
        """Add $ prefix to variable references in text for SugarCube display."""
        import re
        # Match variable patterns: _varname or object.property
        # Don't modify if already has $
        def replace_var(match):
            var_ref = match.group(0)
            if var_ref.startswith('$'):
                return var_ref
            return f'${var_ref}'
        
        # Match: _word or known_object.property
        pattern = r'(?<![$\w])(_\w+|\b(?:player|goblin)\.\w+)'
        return re.sub(pattern, replace_var, text)
    
    def format_dialogue(self, character: str, text: str, parenthetical: str = None) -> str:
        """Format dialogue in bold Markdown."""
        if parenthetical:
            return f"**{character}** {parenthetical}: {text}"
        return f"**{character}**: {text}"
    
    def format_asset(self, asset_type: str, data: str) -> str:
        """Format asset directive as macro."""
        if asset_type.upper() == "BG":
            return f'<<run $(\'body\').addClass(\'{data}\')>>'
        elif asset_type.upper() == "SHOW":
            return f'<img src="{data}.png">'
        elif asset_type.upper() == "MUSIC":
            return f'<<audio "{data}" play>>'
        elif asset_type.upper() == "SFX":
            return f'<<audio "{data}" play>>'
        else:
            return f"<!-- Asset: {asset_type}: {data} -->"
    
    def format_state_change(self, expression: str) -> str:
        """Format state change as <<set>> macro."""
        # Transform expression to add $ prefixes
        transformed = self.transform_expression(expression)
        
        # Normalize operators
        transformed = transformed.replace(' to ', ' = ')
        
        return f"<<set {transformed}>>"
    
    def format_logic_start(self, condition: str) -> str:
        """Format IF as macro."""
        transformed = self.transform_condition(condition)
        return f"<<if {transformed}>>"
    
    def format_logic_elif(self, condition: str) -> str:
        """Format ELIF as macro."""
        transformed = self.transform_condition(condition)
        return f"<<elseif {transformed}>>"
    
    def format_logic_else(self) -> str:
        """Format ELSE as macro."""
        return "<<else>>"
    
    def format_logic_end(self) -> str:
        """Format END as macro."""
        return "<<endif>>"
    
    def format_decision(self, text: str) -> str:
        """Format decision prompt (just text in Twee)."""
        return text
    
    def format_choice(self, label: str, text: str, target: str) -> str:
        """Format a choice option."""
        # Twee format: [[Label|Target]]
        # We strip the # prefix from target if present for Twee compatibility
        if target:
            safe_target = target.replace("#", "").replace(" ", "_").replace(".", "_")
            if text and text != label:
                return f"[[{text}|{safe_target}]]"
            else:
                return f"[[{label}|{safe_target}]]"
        else:
            return f"[[{label}]]"
    
    def format_jump(self, target: str) -> str:
        """Format jump as a clickable link instead of auto-goto to allow text to display."""
        safe_target = target.replace(" ", "_").replace(".", "_")
        # Use a clickable link so text displays before transition
        return f"[[Continue|{safe_target}]]"
