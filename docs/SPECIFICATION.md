Fountain-Flow Specification (v1.0)
Extension: .fflow
Base Standard: Fountain 1.1
1. Introduction
Fountain-Flow is a superset of the Fountain markup language designed for interactive narratives, visual novels, and RPGs.
It adheres to the "Invisible Syntax" philosophy: a raw .fflow file should be readable as a standard screenplay, while containing strict logic for state management, branching, and asset control.
2. Document Structure
2.1 Frontmatter (State Definition)
Every .fflow document may optionally begin with a generic YAML-style frontmatter block to define initial state.
Symbol: $$ for parent, $ for child attribute attribute is called in the text as $parent.attribute
Location: Must be at the very top of the file.
Termination: The block ends with ===.
code
Fountain
$ THEME: Noir
$$Player
    $ PLAYER_HP: 100
    $ PLAYER_ATK: 5
    $ PLAYER_GOLD: 0
    $ PLAYER_INVENTORY: []
    $ PLAYER_MAX_HP: 100
    $ PLAYER_MAX_ATK: 5
    $ PLAYER_MAX_GOLD: 0
    $ PLAYER_MAX_INVENTORY: []
$ RELATIONSHIP_EVE: 50
===
3. Flow Control
3.1 Scenes & Labels
Fountain-Flow utilizes standard Fountain Scene Headings and Section Headings as Jump Anchors.
Scene Heading: INT. BAR - NIGHT (Implicit Anchor)
Section Heading: # BAR_FIGHT (Explicit Anchor)
3.2 Jumps (GOTO)
To move the player to a different scene or label without a choice.
Syntax: ->Text to display-> #TARGET_LABEL
code
Fountain
->The door slams shut-> #GAME_OVER.
3.3 Loops
Syntax: (LOOP: condition)
code
Fountain
(LOOP: $player.hp > 0)
    ~ $player.hp -= 1

    (IF: $player.hp <= 0)
        -> #GAME_OVER
    (END)


3.5 Conditional Blocks
Logic gates that determine if a block of text or events should execute.
Syntax: (IF: condition), (ELIF: condition), (ELSE), (END)
Parsing: These look like Fountain parentheticals but are treated as control flow.
code
Fountain
EVE
(IF: $RELATIONSHIP_EVE > 50)
    I trust you.
(ELSE)
    Don't come any closer.
(END)

## 4. Interaction (The Decision Tree)

### 4.1 Choice Syntax

FFlow supports three choice formats for different use cases:

**Option 1: Decision Menu Choice** (with separate description text)
```fountain
? What do you do?

+ [Attack] Strike first with your sword.
    ~ $ENEMY_HP -= 10
    -> #COMBAT_START

+ [Talk] Try to negotiate peacefully.
    (IF: $CHARISMA > 5)
    -> #PEACEFUL_RESOLUTION
    (ELSE)
    -> #FAILED_NEGOTIATION

+ [Flee] Run away from the danger. -> #CHASE_SCENE
```
- **Format**: `+ [Label] Description text -> #Target`
- **Use when**: You want a decision prompt with detailed choice descriptions
- **Transpilation**: Description text may be lost in Twee (uses only label)

**Option 2: Inline Choice** (Twee-compatible)
```fountain
You see two doors: [Go Left|Left_Room] or [Go Right|Right_Room]
```
- **Format**: `[Label|Target]`
- **Use when**: Embedding choices in narrative text, Twee compatibility needed
- **Transpilation**: Perfect roundtrip fidelity with Twee `[[Label|Target]]`

**Option 3: Implicit Choice** (text with jump)
```fountain
The door slams shut -> #GAME_OVER
```
- **Format**: `Text -> #Target`  
- **Use when**: Single-path narrative jumps with display text
- **Transpilation**: Converts to standard Twee link
4. State Management

**IMPORTANT: Variable Reference Syntax**
- All variable references in expressions, conditions, and state changes MUST use the `$` prefix
- This ensures compatibility with transpilation targets (Twee/SugarCube) and roundtrip fidelity
- Examples: `$RELATIONSHIP_EVE > 50`, `$player.hp += 10`, `$CHAPTER_02_COMPLETE = true`

4.1 State Changes
To modify a variable's value during the flow.
Symbol: ~
Syntax: ~ $VARIABLE_NAME operator value
Examples:
code
Fountain
~ $RELATIONSHIP_EVE += 10
~ $player.hp -= 5
~ $CHAPTER_02_COMPLETE = true
~ $_damage = random(3, $player.atk)
~ INVENTORY.remove("Unknown Potion")
4.2 Local Variables
Syntax: ~ _variable = value
code
Fountain
~ _damage = random(3,$player.atk)
~ $goblin.hp -= _damage

5.3 Randomization
Syntax: ~ variable = random(min, max)
code
Fountain
~ _damage = random(3,$player.atk)
~ $goblin.hp -= _damage


6. Asset Injection (Media)
Standard Fountain relies on the reader's imagination. Fountain-Flow explicitly dictates audiovisual assets using the "Bang" operator.
Symbol: !
6.1 Backgrounds
Syntax: ! BG: asset_id
code
Fountain
INT. ABANDONED MALL - NIGHT
! BG: mall_ruins_dark
6.2 Character Sprites (Paper Dolls)
Syntax: ! SHOW: character_id, expression, [position]
Syntax: ! HIDE: character_id
code
Fountain
! SHOW: eve, angry, left
! SHOW: adam, nervous, right

EVE
Why did you do it?
6.3 Audio & VFX
Syntax: ! MUSIC: track_id, [loop|once]
Syntax: ! SFX: sound_id
code
Fountain
! MUSIC: tension_theme, loop
! SFX: glass_shatter
7. Backward Compatibility
A key feature of Fountain-Flow is that it degrades gracefully.
Standard Parsers: If a .fflow file is opened in Highland 2, Slugline, or 'Fountain Mode', the logic lines (~, !, ?) should be treated as Action lines.
Recommendation: When transpiling to a "Clean PDF" for voice actors, all lines starting with !, ~, ?, $ and blocks inside (IF:...) should be stripped or commented out (Boneyard).

8. Engine Implementation Notes
8.1 State Management
The engine must maintain a persistent state object (e.g., JSON) that is updated by the ~ operator.
8.2 Asset Handling
When the engine encounters an ! operator, it must look up the asset_id in a local asset manifest (e.g., assets.json) to retrieve the file path.
8.3 Choice Processing
When the engine encounters a ? operator, it must pause execution and display the subsequent + options to the user. The engine must wait for user input before proceeding.
8.4 Conditional Logic
The engine must evaluate the condition in (IF:...) and only execute the subsequent block if the condition is true.
8.5 Loops
The engine must evaluate the condition in (LOOP:...) and only execute the subsequent block if the condition is true. The engine must repeat the block until the condition is false.
8.6 Randomization
The engine must generate a random number between the min and max values in random(min, max).

9. Fountain Markup
9.1 Standard Fountain Elements
Fountain-Flow supports all standard Fountain markup elements, including:

Scene Headings: INT. LOCATION - DAY

Action Lines: The hero walks down the street.

Character Names: EVE

Dialogue: "Hello, world."

Parentheticals: (whispering)

Section Headings: # SECTION_NAME

9.2 Fountain-Flow Specific Elements
Fountain-Flow adds the following elements to standard Fountain:

State Definition: $$ for parent, $ for child attribute

Jumps: Text to display-> #TARGET_LABEL

Loops: (LOOP: condition)

Conditional Blocks: (IF: condition), (ELIF: condition), (ELSE), (END)

Choice Menus: ? for prompt, + for option

Variable Mutation: ~

Randomization: random(min, max)

Asset Injection: ! BG:, ! SHOW:, ! HIDE:, ! MUSIC:, ! SFX:  