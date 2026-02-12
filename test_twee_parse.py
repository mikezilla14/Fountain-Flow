import sys
sys.path.insert(0, 'src')

from reverse_parser import TweeParser

twee_sample = ''':: StoryInit
<<set $player to { name: "Hero", maxHP: 20, hp: 20, atk: 5, gold: 0 }>>
<<set $goblin to { name: "Fetral", maxHP: 10, hp: 10, atk: 3, gold: 7 }>>

:: Start
You wake up in a forest, sword in hand. A goblin blocks the path.
What do you do?
[[Check Self|Player_Status]]
[[Check Enemy|Goblin_Status]]'''

parser = TweeParser()
ast = parser.parse(twee_sample)

print(f'Parsed {len(ast)} nodes')
for i, node in enumerate(ast):
    print(f'{i}: {type(node).__name__}', end='')
    if hasattr(node, 'text'):
        print(f' - text={node.text!r}', end='')
    if hasattr(node, 'anchor'):
        print(f' - anchor={node.anchor!r}', end='')
    if hasattr(node, 'expression'):
        print(f' - expr={node.expression!r}', end='')
    if hasattr(node, 'label'):
        print(f' - label={node.label!r}', end='')
    print()
