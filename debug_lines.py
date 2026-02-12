import sys
sys.path.insert(0, 'src')

from fountain_flow.parser.fflow import parse

# Read the actual file
content = open('output/fantasy_3.fflow', encoding='utf-8').read()
lines = content.split('\n')

# Find lines with choices
for i, line in enumerate(lines):
    if '+ [' in line:
        print(f"Line {i+1}: {repr(line)}")
        # Try parsing just this line
        ast = parse(line)
        if ast:
            node = ast[0]
            print(f"  -> Parsed as: {type(node).__name__}")
            if hasattr(node, '__dict__'):
                print(f"  -> Attributes: {node.__dict__}")
        print()
