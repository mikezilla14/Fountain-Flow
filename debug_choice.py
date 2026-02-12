import sys
sys.path.insert(0, 'src')

from fountain_flow.languages.fflow import FFlowLanguage

lang = FFlowLanguage()

print("All choice-related patterns:")
choice_patterns = [p for p in lang.patterns if 'choice' in p.name.lower()]
for p in choice_patterns:
    print(f"  Name: {p.name}")
    print(f"  Priority: {p.priority}")
    print(f"  Regex: {p.regex}")
    print()

# Test the pattern
import re
test_line = "+ [Fight] Fight the goblin. -> #Fight"
print(f"Testing line: {test_line}")
print()

for p in sorted(lang.patterns, key=lambda x: -x.priority):
    match = p.match(test_line)
    if match:
        print(f"MATCH! Pattern: {p.name} (priority {p.priority})")
        print(f"  Groups: {match.groups()}")
        break
else:
    print("NO MATCH from any pattern")
