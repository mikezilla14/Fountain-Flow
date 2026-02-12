from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any

@dataclass
class ScriptNode:
    """Base class for all AST nodes."""
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}

@dataclass
class FrontmatterNode(ScriptNode):
    """Represents the initial configuration block."""
    variables: Dict[str, Any] = field(default_factory=dict)
    depth: int = 0

@dataclass
class SceneHeadingNode(ScriptNode):
    """Standard Fountain Scene Heading (INT./EXT.)."""
    scene_id: str  # Auto-generated or explicit
    text: str
    depth: int = 0

@dataclass
class SectionHeadingNode(ScriptNode):
    """Section Heading used as anchor (# SCENE_NAME)."""
    text: str
    anchor: str
    depth: int = 0

@dataclass
class ActionNode(ScriptNode):
    """Descriptive text."""
    text: str
    depth: int = 0

@dataclass
class DialogueNode(ScriptNode):
    """Character name and dialogue."""
    character: str
    text: str
    parenthetical: Optional[str] = None
    depth: int = 0

@dataclass
class AssetNode(ScriptNode):
    """Asset injection (! TYPE: id)."""
    asset_type: str
    data: str
    depth: int = 0

@dataclass
class StateChangeNode(ScriptNode):
    """Variable mutation (~ VAR = VAL)."""
    expression: str
    depth: int = 0

@dataclass
class LogicNode(ScriptNode):
    """Logic block wrapper (IF/ELSE/END)."""
    start_condition: Optional[str] = None  # content of (IF: ...)
    is_elif: bool = False
    is_else: bool = False
    is_end: bool = False
    depth: int = 0

@dataclass
class DecisionNode(ScriptNode):
    """Decision prompt (? Prompt)."""
    text: str
    depth: int = 0

@dataclass
class ChoiceNode(ScriptNode):
    """Interactive choice (+ [Label] Text -> #TARGET)."""
    label: str
    text: str
    target: str
    conditions: List[str] = field(default_factory=list) # For (IF:...) inside choices
    depth: int = 0

@dataclass
class JumpNode(ScriptNode):
    """Direct jump (-> #TARGET)."""
    target: str
    depth: int = 0

# Type alias for list of nodes
ScriptAST = List[ScriptNode]
