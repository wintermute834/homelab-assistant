# Text-Based Adventure Game

A highly extensible text-based adventure game with a rich world, multiple areas, NPCS, quests, and gameplay mechanics.

## Overview

Game features:
- **5x5 map** large area to explore with lots of interesting locations
- **10+ different items** with properties and effects
- **5+ NPCS** with dialogue trees, quest-giving capabilities, and items/rewards
- **5+ quests** (1 main quest, 4 side quests)
- **Combat system** with multiple enemy types
- **Save/load functionality** with full state preservation
- **Hint system** for players who need help

## Game World

### Unique Areas
1. **Forest Clearing** - Starting point, meets Old Traveler
2. **Dark Forest** - Wolf encounter, requires torch
3. **Stone Gate** - Puzzle requiring key and torch
4. **Secret Sanctuary** - Final area with ancient gem
5. **Village** - Merchant, supplies, tavern
6. **Grove** - Healing herbs, Wise Owl
7. **Cave** - Mysterious Stranger
8. **Ancient Ruins** - Inscryptions of an ancient peoples
9. **Mountain Path** - Bear encounter
10. **Lake Shore** - Resting place
11. **Hidden Library** - Secret area accessible with rune power

### Items
- **Unlit Torch** - A stump of wood that could be useful if you can light it.
- **Torch** - Light up the darkness.
- **Wolf Pelt** - The pelt of a slain wolf. Perhaps it will fetch a pretty penny.
- **Key** - A rusted iron key, who knows what it unlocks.
- **Health Potion** - A small, spherical potion brimming with pink liquid. Restores 25 HP.
- **Ancient Gem** - A legendary artifact, and the final reward of your journey.
- **Gate Token** - Proof of passage.
- **Herb** - A handful of leafy herbs. Restores 10 HP.
- **Map** - Crinkled parchment details the layout of the forest you have explored.
- **Shield** - A heavy wooden buckler. Reduces damage taken by 5.
- **Sword** - Iron tempered in fire to kill. Increases attack power by 5.
- **Rune Stone** - Ancient runes left by a mysterious civilization. Grants the power of the forest.
- **Coins** - Currency. Can be used at the merchant to buy items

### NPCS
- **Old Traveler** - Gives main quest
- **Forest Spirit** - Appears after first wolf is defeated
- **Merchant** - Sells healing, battle, and quest items for gold
- **Ancient Guardian** - Guards the sanctuary, a series of riddles are required to pass
- **Mysterious Stranger** - Offers rune power
- **Wise Owl** - Gives herbalist quest

### Quests
1. **The Path to the Sanctuary** (Main) - Find your way to the sanctuary
2. **The Herbalist's Request** (Side) - Gather 3 healing herbs
3. **Ruins of the Past** (Side) - Explore ruins and find rune stone
4. **Forest Champion** (Side) - Defeat all forest creatures
5. **The Hidden Library** (Side) - Discover the secret library

## How to Play

### Starting the Game
```bash
python main.py
```

### Commands
- `go [direction]` - Move (north, south, east, west, back)
- `examine [item]` - Examine item or area
- `take [item]` - Pick up item
- `use [item]` - Use item
- `talk [npc]` - Talk to NPC
- `attack` - Attack enemy
- `open` - Open door/container
- `inventory` - View inventory
- `quests` - View quests
- `hint` - Get contextual hint
- `help` - Show command list
- `save` - Save game
- `load` - Load game
- `quit` - Exit game

### Example Gameplay
```
> examine
You are in a forest clearing, dappled by sunlight.

In all directions, dense woods encircle you.

Leaning against the path to the north is a hunched old man, an unlit torch lies by his feet.
> talk old_traveler
Hello young adventurer, do you wish to unravel the secrets of these woods?

Take this torch and ventue out into the unknown.

You must discover and break in to the sanctuary at the heart of these woods!

Got item: Unlit Torch
> go north
You enter the thick woods, following a small trail, likely created by some animal.

Out of nowhere, a wolf attacks!

You take 10 damage!
Health: 90/100
> attack
You dealt 10 damage. The enemy has 20 HP left...

You take 10 damage!
Health: 80/100
> attack
You dealt 10 damage. The enemy has 10 HP left...

You dodge the attack! Nice moves
Health: 80/100
> attack
You dealt 10 damage. You defeated the wolf!

Got item: Wolf Pelt

In its lair, you discover a key...
> take key
You picked up the Iron Key.

...
```

## Architecture

The game uses a modular architecture, designed to be highly extensible.

- **main.py** - Game loop, rendering, save/load
- **player.py** - Player stats, inventory, quests
- **scene.py** - Scene class for locations
- **scenes.py** - All scene definitions
- **items.py** - Item class and definitions
- **npcs.py** - NPC class and definitions
- **quests.py** - Quest class and definitions
- **game_state.py** - Global state, achievements, settings

This separation of modules makes it easy to modify individual components without affecting others.

## File Structure

```
adventure/
├── main.py          # Game loop and rendering
├── player.py        # Player class
├── scene.py         # Scene class
├── scenes.py        # Scene definitions
├── items.py         # Item class and definitions
├── npcs.py          # NPC class and definitions
├── quests.py        # Quest class and definitions
├── game_state.py    # Game state and achievements
├── test_game.py     # Test suite
├── test_imports.py  # Import verification
└── README.md        # This file
```

## Testing

Run the test suite:
```bash
python test_game.py
```

Run import verification:
```bash
python simple_test.py
```
