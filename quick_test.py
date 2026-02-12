"""Quick manual test of the refactored parser"""

import sys
sys.path.insert(0, 'src')

from core_parser import parse

# Test basic FFlow parsing
test_script = """$ HP: 100
===

INT. BAR - NIGHT
Action line.

JOHN
Hello there.

~ HP += 5
-> #END
"""

try:
    nodes = parse(test_script)
    print(f"✓ Parsing successful: {len(nodes)} nodes created")
    for i, node in enumerate(nodes):
        print(f"  {i}: {type(node).__name__}")
    print("\nTest PASSED!")
except Exception as e:
    print(f"✗ Parsing failed: {e}")
    import traceback
    traceback.print_exc()
