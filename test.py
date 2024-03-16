import asyncio

from pokemon import Pokemon, Team

selected_format = 'gen3ou'


async def fetch_game_data(match_number):
    file_name = f"replay_{match_number:02d}.txt"  # Format the match number properly
    with open(file_name, 'r') as file:
        game_log = file.read()  # Read the entire file at once

    username = extract_username(game_log)
    parse_battle_log(game_log)

    # if username:
    #     team_details = extract_pokemon(game_log, username)
    #     pokemons = [
    #         Pokemon(
    #             name=pkmn['name'],
    #             ability=pkmn.get('ability', 'Unknown'),
    #             item=pkmn.get('item', 'None'),
    #             moveset=pkmn['moveset']
    #         ) for pkmn in team_details
    #     ]
    #     team = Team(username, pokemons)
    #     print(team)
    #     return team


def extract_username(log):
    for line in log.split("\n"):
        if "Processing player:" in line:
            return line.split("Processing player:")[1].strip()


def extract_pokemon2(game_log, username):
    player_names = []

    for line in game_log.split("\n"):
        if "|player|" in line:
            parts = line.split("|")
            if len(parts) >= 4:
                # Append player name to the list
                player_names.append(parts[3])

    # Ensure we have either one or two player names captured
    player1_name = player_names[0] if len(player_names) > 0 else "Unknown Player 1"
    player2_name = player_names[1] if len(player_names) > 1 else "Unknown Player 2"

    print(f"Player 1: {player1_name}")
    print(f"Player 2: {player2_name}")

    # Return an empty string as the placeholder for team details to maintain the function's structure
    return ""


def parse_battle_log(game_log):
    # Initialize the main data structure
    battle_data = {
        "players": {},
        "turns": [],
        "winner": None
    }

    # Split the log into lines for processing
    lines = game_log.split("\n")

    # Process each line
    for line in lines:
        parts = line.split("|")

        # Skip empty parts
        if len(parts) < 2:
            continue

        action = parts[1]

        # Player identification
        if action == "player":
            player_id, player_name = parts[2], parts[3]
            battle_data["players"][player_id] = {"name": player_name, "team": []}

        # Pokémon switch in (also captures initial team setup)
        elif action == "switch":
            player_id = parts[2].split(":")[0]
            pokemon_name = parts[3].split(",")[0]
            if pokemon_name not in battle_data["players"][player_id]["team"]:
                battle_data["players"][player_id]["team"].append(pokemon_name)

        # Turn-based actions
        elif action == "turn":
            turn_number = int(parts[2])
            battle_data["turns"].append({"turn": turn_number, "actions": []})

        # Actions within turns
        elif action in ["move", "faint", "-ability", "-item", "-damage", "-heal", "-status"]:
            if "turns" in battle_data and battle_data["turns"]:
                battle_data["turns"][-1]["actions"].append(line)

        # Battle outcome
        elif action == "win":
            winner_name = parts[2]
            battle_data["winner"] = winner_name

    return battle_data


async def main():
    games = range(1, 6)  # Match IDs from 1 to 5
    for match_id in games:
        await fetch_game_data(match_id)


if __name__ == "__main__":
    matches = range(1, 6)  # Match IDs from 1 to 5
    all_teams = []  # List to store all teams

    print("============ STARTING TEST ============")
    asyncio.run(main())
    print("============ FINISHING TEST ============")
    exit()
