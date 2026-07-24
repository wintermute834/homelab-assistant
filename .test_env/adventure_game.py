"""
A text-based adventure game built with Python.

This is a modular design meant to be easily expanded. The core systems are:
- GameState: manages player stats and inventory
- Scene: defines locations and their descriptions/actions
- Commands: parses user input and executes actions
- Main loop: ties everything together

To expand:
- Add more complex inventory (stacking, combining)
- Implement dialogue trees or NPC interactions
- Add multiple endings based on choices
- Include save/load functionality
- More detailed descriptions and lore
- Combat system
- Puzzle solving mechanics
"""


# =============================================================================
# CORE GAME STATE
# =============================================================================

class GameState:
    """
    Manages player stats and inventory.
    
    This class is intentionally kept small and focused on player data only.
    For expansion, you could add:
    - Level/experience system
    - Equipment slots with stats
    - Quest tracker
    - Flags for game state (e.g., "game_over", "completed")
    """
    
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.MAX_STACKS = {}
        self.inventory = {}  # {item_name: quantity}
        self.torch_lit = False
        self.key = False
        self.visited = set()
        self.current_enemy = None
        self.enemy_health = 0
        self.in_combat = False
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
            return True  # Game over
        return False
        
    def heal(self, amount):
        self.health = min(self.health + amount, self.max_health)
        
    def acquire_item(self, item_name, quantity=1):
        max_stack = self.MAX_STACKS.get(item_name, 99)  # default unlimited
        if quantity > max_stack:
            quantity = max_stack
        
        if item_name in self.inventory:
            if self.inventory[item_name] + quantity > max_stack:
                return False  # Can't fit more
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity
        
        return True

    def use_item(self, item_name):
        """Use an item from inventory. Returns success or None."""
        if item_name not in self.inventory:
            return False
        
        qty = self.inventory.pop(item_name)
        
        # Item effects go here - keep simple for now
        if item_name == "health_potion":
            self.heal(20)
        elif item_name == "torch":
            self.torch_lit = True
        elif item_name == "key":
            self.key = True
            
        return True
        
    def get_inventory(self):
        items = []
        for name, qty in self.inventory.items():
            if qty > 1:
                items.append(f"{name} (x{qty})")
            else:
                items.append(name)
        return ", ".join(items) if items else "empty"


# =============================================================================
# SCENE SYSTEM
# =============================================================================

class Scene:
    """
    Represents a location in the game world.
    
    To expand:
    - Add NPC objects with dialogue trees
    - Add puzzle conditions
    - Track visited scenes or flags
    - Store lore/history per scene
    """
    
    def __init__(self, name, description, actions=None):
        self.name = name
        self.description = description
        self.actions = actions if actions else []
        
    def can_act(self, action_name):
        return any(a["name"] == action_name for a in self.actions)
        
    def get_action(self, action_name):
        for a in self.actions:
            if a["name"] == action_name:
                return a
        return None


# =============================================================================
# COMMAND HANDLERS
# =============================================================================

def handle_move(cmd, state, current_scene, scene_registry):
    """Handle movement commands. Returns new scene or None."""
    direction = cmd.get("direction")
    
    if not current_scene.can_act(direction):
        return None
        
    # Find the destination scene from registry
    dest_name = current_scene.actions[0]["dest"]  # Simplified: one direction per scene
    return scene_registry.get(dest_name)


def handle_examine(cmd, state, current_scene):
    """Handle examine/look commands."""
    return current_scene.description


def handle_use(cmd, state, current_scene):
    """Handle use commands."""
    item = cmd.get("item")
    if not item:
        return "You don't have that item."
        
    success = state.use_item(item)
    if success:
        return f"You used {item}."
    else:
        return f"You don't have {item}."


def handle_inventory(cmd, state):
    """Handle inventory commands."""
    return state.get_inventory()


def handle_take(cmd, state, current_scene):
    """Handle take commands."""
    item = cmd.get("item")
    if not item:
        return "You don't have that item."
        
    success = state.acquire_item(item)
    if success:
        return f"You took {item}."
    else:
        return f"There is no {item} here to take."


def handle_drop(cmd, state):
    """Handle drop commands."""
    item = cmd.get("item")
    if not item:
        return "You don't have that item."
        
    success = state.inventory.pop(item, None)
    if success:
        return f"You dropped {item}."
    else:
        return f"You don't have {item}."


def handle_talk(cmd, state, current_scene):
    """Handle talk commands."""
    npc = cmd.get("npc") if cmd else None
    if npc:
        return f"You spoke to {npc}."
    # Fall back to scene NPC if any
    for action in current_scene.actions:
        if action.get("npc"):
            return f"The {action['npc']} says: ..."
    return "You have nothing to say."


def handle_attack(cmd, state, current_scene):
    """Handle attack commands."""
    # Combat logic would go here
    if state.current_enemy and state.in_combat:
        damage = 10  # Simplified: fixed damage for now
        state.enemy_health -= damage
        if state.enemy_health <= 0:
            state.current_enemy = None
            state.enemy_health = 0
            state.in_combat = False
            return "You defeated the enemy!"
        return f"You dealt {damage} damage. The enemy has {state.enemy_health} HP left."
    return "There is no enemy to attack right now."


# =============================================================================
# SCENE REGISTRY
# =============================================================================

SCENES = {
    "forest_clearing": Scene(
        name="Forest Clearing",
        description="You stand in a sun-dappled clearing surrounded by ancient oaks. "
                    "A narrow path leads north toward a dark forest, while to the "
                    "east you see what might be a stone gate.\n\n*An old traveler sits nearby, offering cryptic advice.*",
        actions=[
            {"name": "north", "dest": "dark_forest"},
            {"name": "east", "dest": "stone_gate"},
            {"name": "talk to traveler", "dest": "forest_clearing", "npc": "Old Traveler"},
        ],
    ),
    
    "dark_forest": Scene(
        name="Dark Forest",
        description="The trees here are thick and twisted. Shadows seem to move on their own. "
                    "You hear the occasional snap of a twig, but nothing seems close.\n\n*An ominous presence lurks in the shadows.*",
        actions=[
            {"name": "south", "dest": "forest_clearing"},
        ],
    ),
    
    "stone_gate": Scene(
        name="Stone Gate",
        description="A massive stone gate blocks your path. Carved into its surface is the "
                    "faint outline of a keyhole. The gate seems to be locked.\n\n*The gate bears ancient carvings hinting at a forgotten ritual.*\n\n*A puzzle: the gate requires both a key and a lit torch to open.*",
        actions=[
            {"name": "west", "dest": "forest_clearing"},
            {"name": "open", "type": "puzzle"},
        ],
    ),
}


# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def render_scene(scene, state):
    """Render the current scene with player stats."""
    print("\n" + "-" * 40)
    print(f"Location: {scene.name}")
    print(scene.description)
    print("-" * 40)
    
    if getattr(state, 'torch_lit', False):
        print(f"[Torch lit]")
    else:
        print("[No torch lit]")
        
    if "health_potion" in state.inventory:
        print(f"[Health potion x{state.inventory['health_potion']}]")
    if getattr(state, 'key', False):
        print("[You have a key]")
    
    print("-" * 40)


def main():
    # Initialize game state
    state = GameState()
    current_scene = SCENES["forest_clearing"]
    
    # Set torch_lit flag for demo purposes
    state.torch_lit = False
    
    print("\n" + "=" * 40)
    print("Welcome to the Adventure!")
    print("=" * 40)
    print("\nYou wake up in a forest clearing, with no memory of how you got here.")
    print("\nCommands: go [direction], examine, take [item], use [item], inventory, drop [item]")
    
    render_scene(current_scene, state)
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input.lower() == "quit":
                # Parse command
                parts = user_input.split(None, 1)  # Split into verb and optional rest
                verb = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                # Handle commands
                if verb == "go":
                    direction = args.lower()
                    new_scene = handle_move({"direction": direction}, state, current_scene, SCENES)
                    if new_scene:
                        current_scene = new_scene
                        # Spawn enemy when entering dark forest
                        if new_scene.name == "dark_forest" and state.current_enemy is None:
                            state.current_enemy = "wolf"
                            state.enemy_health = 30
                            state.in_combat = True
                        render_scene(current_scene, state)
                    else:
                        print("You can't go that way.")
                        
                elif verb in ("examine", "look"):
                    result = handle_examine(None, state, current_scene)
                    print(result)
                    
                elif verb == "take":
                    item = args.lower()
                    result = handle_take({"item": item}, state, current_scene)
                    print(result)
                    
                elif verb == "use":
                    item = args.lower()
                    result = handle_use({"item": item}, state, current_scene)
                    print(result)
                    
                elif verb == "inventory":
                    print(state.get_inventory())
                    
                elif verb == "talk":
                    result = handle_talk(None, state, current_scene)
                    print(result)
                    
                elif verb == "attack":
                    result = handle_attack(None, state, current_scene)
                    print(result)
                    
                elif verb == "open":
                    # Puzzle: requires key and torch
                    if state.key and state.torch_lit:
                        print("The gate creaks open! You pass through.")
                        # Give a reward item
                        state.acquire_item("gate_token")
                    else:
                        if not state.key:
                            print("You need a key to open this gate.")
                        elif not state.torch_lit:
                            print("The gate is too dark without a torch lit. Use the torch first.")
                elif verb == "drop":
                    item = args.lower()
                    result = handle_drop({"item": item}, state)
                    print(result)
                    
                else:
                    print("I don't understand that command.")
                    
        except EOFError:
            # End of game - show appropriate ending based on choices
            if state.visited:
                print("\n--- ENDINGS ---")
                if "dark_forest" in state.visited and state.key:
                    print("You opened the gate, but the shadows claimed you. (Bad ending)")
                elif "forest_clearing" in state.visited and not state.torch_lit:
                    print("You wandered forever, lost in the dark. (Bad ending)")
                else:
                    print("You survived the forest and found peace. (Good ending)")
            break


# Save/Load functionality
import json

def save_game(filename="adventure_save.json"):
    """Save the current game state."""
    data = {
        "state": {
            "health": state.health,
            "max_health": state.max_health,
            "inventory": state.inventory,
            "torch_lit": state.torch_lit,
            "key": state.key,
            "visited": list(state.visited),
        },
        "current_scene": current_scene.name,
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def load_game(filename="adventure_save.json"):
    """Load a saved game."""
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        # Reset state
        global state, current_scene
        state = GameState()
        state.health = data["state"]["health"]
        state.max_health = data["state"]["max_health"]
        state.inventory = data["state"]["inventory"]
        state.torch_lit = data["state"]["torch_lit"]
        state.key = data["state"]["key"]
        state.visited = set(data["state"]["visited"])
        current_scene = SCENES[data["current_scene"]]
        print("Game loaded successfully.")
        return True
    except FileNotFoundError:
        print("No save file found. Starting fresh.")
        return False


if __name__ == "__main__":
    main()
