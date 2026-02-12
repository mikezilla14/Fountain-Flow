import sys
sys.path.insert(0, 'src')

from fountain_flow.parser.fflow import parse

# Test the problematic line
test_lines = [
    "Fall to the ground... -> #Game_Over",
    "    Fall to the ground... -> #Game_Over",  # With indentation
]

for line in test_lines:
    print(f"Testing: {repr(line)}")
    ast = parse(line)
    for node in ast:
        print(f"  -> {type(node).__name__}: {node.__dict__}")
    print()
