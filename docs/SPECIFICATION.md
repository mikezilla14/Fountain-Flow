Fountain-Flow Specification (v1.0)
Extension: .fflow
Base Standard: Fountain 1.1
1. Introduction
Fountain-Flow is a superset of the Fountain markup language designed for interactive narratives, visual novels, and RPGs.
It adheres to the "Invisible Syntax" philosophy: a raw .fflow file should be readable as a standard screenplay, while containing strict logic for state management, branching, and asset control.
2. Document Structure
2.1 Frontmatter (State Definition)
Every .fflow document may optionally begin with a generic YAML-style frontmatter block to define initial state.
Symbol: $
Location: Must be at the very top of the file.
Termination: The block ends with ===.
code
Fountain
$ THEME: Noir
$ PLAYER_HP: 100
$ INVENTORY: []
$ RELATIONSHIP_EVE: 50
===
3. Flow Control
3.1 Scenes & Labels
Fountain-Flow utilizes standard Fountain Scene Headings and Section Headings as Jump Anchors.
Scene Heading: INT. BAR - NIGHT (Implicit Anchor)
Section Heading: # BAR_FIGHT (Explicit Anchor)
3.2 Jumps (GOTO)
To move the player to a different scene or label without a choice.
Syntax: -> #TARGET_LABEL
code
Fountain
The door slams shut.

-> #GAME_OVER
3.3 Conditional Blocks
Logic gates that determine if a block of text or events should execute.
Syntax: (IF: condition), (ELIF: condition), (ELSE), (END)
Parsing: These look like Fountain parentheticals but are treated as control flow.
code
Fountain
EVE
(IF: RELATIONSHIP_EVE > 50)
    I trust you.
(ELSE)
    Don't come any closer.
(END)
4. Interaction (The Decision Tree)
4.1 Choice Menus
A block of choices presented to the player.
Prompt: Starts with ?
Option: Starts with +
Action: Uses -> for jumps or ~ for immediate state changes.
code
Fountain
? How do you react?

+ [Attack] Strike first.
    ~ ENEMY_HP -= 10
    -> #COMBAT_START

+ [Talk] "Can we discuss this?"
    (IF: CHARISMA > 5)
    -> #PEACEFUL_RESOLUTION
    (ELSE)
    -> #FAILED_NEGOTIATION

+ [Flee] Run away. -> #CHASE_SCENE
5. State Management
5.1 Variable Mutation
Modifying the game state during the narrative flow.
Symbol: ~
Behavior: Supports standard operators (=, +=, -=, ++, --).
code
Fountain
The potion tastes bitter.
~ HP -= 5
~ INVENTORY.remove("Unknown Potion")
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