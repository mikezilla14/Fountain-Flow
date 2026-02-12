# Fidelity Error Reduction Summary

## Progress: 33 → 25 errors ✅

### Fixes Implemented

1. **[[Continue|Target]] Detection** (lines 248-256 in engine.py)
   - Reverse parser now detects "Continue" links as JumpNodes
   - Eliminated 7 JumpNode→ChoiceNode errors

2. **Variable $ Prefix Preservation** (lines 199-211, 265-271 in engine.py)
   - Keep `$` prefixes when parsing Twee→FFlow
   - FFlow supports both `$var` and `var` syntax

3. **Removed Variable Interpolation** (lines 245-258 in twee.py)
   - Don't add `$` to variables in action text during transpilation
   - Preserves original variable format

## Remaining 25 Errors

### Category 1: Variable Formatting Inconsistencies (6 errors)
**Lines:** 4, 6, 8-9, 11-12

**Issue:** Original FFlow is inconsistent with `$` prefix usage:
- Conditionals: `player.hp <= 0` (no `$`)
- State changes: Mixed - some use `$`, some don't
- When transpiled to Twee: ALL get `$` (required by SugarCube)
- Roundtrip back: Has `$` everywhere, doesn't match original

**Example:**
```
Original:  (IF: player.hp <= 0)
Twee:      <<if $player.hp <= 0>>
Roundtrip: (IF: $player.hp <= 0)  ❌ Mismatch!
```

**Status:** ACCEPTABLE formatting difference

### Category 2: Decision Node Detection (5 errors)
**Lines:** 3, 5, 7, 10

**Issue:** `? Prompt text` in FFlow becomes plain text in Twee
- Twee has no decision/prompt syntax
- Reverse parser sees it as ActionNode, not DecisionNode

**Status:** ACCEPTABLE - Twee format limitation

### Category 3: Inline Jump Structural Issues (14 errors)
**Lines:** 13-26

**Issue:** Cascading node misalignment after inline jump `text -> #target`
- Creates structural differences in AST
- Nodes get offset/reordered

**Status:** Needs investigation

## Total Breakdown

- **Acceptable differences:** 11 errors (variables + decisions)
- **Structural issues:** 14 errors (inline jumps)

**Target:** Fix structural issues to get down to ~11 acceptable errors
