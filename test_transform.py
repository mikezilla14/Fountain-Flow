import sys
sys.path.insert(0, 'src')

from languages.twee_language import TweeLanguage

t = TweeLanguage()

tests = [
    ('player.hp += 5', '$player.hp += 5'),
    ('$player.hp > player.maxHP', '$player.hp > $player.maxHP'),
    ('$player.hp = $player.maxHP', '$player.hp = $player.maxHP'),
    ('_damage = random(3,$player.atk)', '$_damage = random(3,$player.atk)'),
    ('random(1, 10)', 'random(1, 10)'),
    ('goblin.hp <= 0', '$goblin.hp <= 0'),
]

print("Transform Expression Tests:")
print("=" * 80)
all_pass = True
for input_expr, expected in tests:
    result = t.transform_expression(input_expr)
    passed = (result == expected)
    all_pass = all_pass and passed
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {input_expr!r}")
    if not passed:
        print(f"  Expected: {expected!r}")
        print(f"  Got:      {result!r}")

print("=" * 80)
print(f"Overall: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
