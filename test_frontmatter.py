import sys
sys.path.insert(0, 'src')

from reverse_parser import TweeParser

# Test just the StoryInit passage to see how frontmatter is being parsed
twee_frontmatter = ''':: StoryInit
<<set $player to { name: "Hero", maxHP: 20, hp: 20, atk: 5, gold: 0 }>>
<<set $goblin to { name: "Fetral", maxHP: 10, hp: 10, atk: 3, gold: 7 }>>'''

parser = TweeParser()
ast = parser.parse(twee_frontmatter)

print(f'Parsed {len(ast)} nodes from StoryInit:')
for i, node in enumerate(ast):
    print(f'{i}: {type(node).__name__}', end='')
    if hasattr(node, 'text'):
        print(f' - text={node.text!r}'[:80], end='')
    if hasattr(node, 'anchor'):
        print(f' - anchor={node.anchor!r}', end='')
    if hasattr(node, 'expression'):
        print(f' - expr={node.expression!r}'[:80], end='')
    if hasattr(node, 'variables'):
        print(f' - variables={node.variables!r}'[:80], end='')
    print()

# Expected: Should have 1 FrontmatterNode with nested objects
# Actual: Probably has SectionHeadingNode + StateChangeNode(s)

print("\n" + "="*80)
print("ISSUE: StoryInit should create FrontmatterNode, not SectionHeadingNode + StateChangeNodes")
print("The Twee parser needs special handling for StoryInit passage")
