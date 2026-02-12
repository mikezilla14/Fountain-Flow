import sys
sys.path.insert(0, 'src')

from fountain_flow.languages.fflow import FFlowLanguage
import re

lang = FFlowLanguage()

# Test both syntaxes
test_lines = [
    "+ [Fight] Fight the goblin. -> #Fight",  # Bracket syntax
    "+ ->Fight the goblin.->#Fight",          # Non-bracket syntax
]

print("Testing both choice syntaxes:")
print()

for line in test_lines:
    print(f"Line: {line}")
    matched = False
    for p in sorted(lang.patterns, key=lambda x: -x.priority):
        match = p.match(line)
        if match:
            print(f"  MATCH! Pattern: {p.name} (priority {p.priority})")
            print(f"  Groups: {match.groups()}")
            matched = True
            break
    if not matched:
        print("  NO MATCH")
    print()
