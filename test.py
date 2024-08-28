import asyncio

from pokemon import Pokemon, Team

selected_format = 'gen3ou'


async def fetch_game_data(match_number):
    file_name = f"replay_{match_number:02d}.txt"
    try:
        with open(file_name, 'r') as file:
            game_log = file.read()

        username = extract_username(game_log)
        if username:
            team_details = extract_pokemon2(game_log, username)  # This returns a list of Pokémon names
            pokemons = [
                Pokemon(
                    name=pkmn,  # Since team_details contains Pokémon names
                    ability='Unknown',  # Default value since details aren't available
                    item='None',  # Default value since details aren't available
                    moveset=[]  # Default empty moveset
                ) for pkmn in team_details
            ]
            team = Team(username, pokemons)
            print(team)
            return team

    except FileNotFoundError:
        print(f"File {file_name} not found.")
        return None


def extract_username(log):
    for line in log.split("\n"):
        if "Processing player:" in line:
            return line.split("Processing player:")[1].strip()


def extract_pokemon2(game_log, username):
    player_names = []
    player_teams = {"p1": [], "p2": []}

    for line in game_log.split("\n"):
        parts = line.split("|")
        if len(parts) < 2:
            continue

        action = parts[1]

        if action == "player":
            player_id, player_name = parts[2], parts[3]
            player_names.append(player_name)

        elif action in ["switch", "drag"]:
            player_id = parts[2][:2]  # Get 'p1' or 'p2'
            pokemon_name = parts[3].split(",")[0]
            if pokemon_name not in player_teams[player_id]:
                player_teams[player_id].append(pokemon_name)

    # Ensure we have either one or two player names captured
    player1_name = player_names[0] if len(player_names) > 0 else "Unknown Player 1"
    player2_name = player_names[1] if len(player_names) > 1 else "Unknown Player 2"

    print(f"Player 1: {player1_name}")
    print(f"Player 2: {player2_name}")

    # Identify the username's player ID (p1 or p2)
    user_player_id = None
    if username == player1_name:
        user_player_id = "p1"
    elif username == player2_name:
        user_player_id = "p2"

    if user_player_id:
        user_team = player_teams[user_player_id]
        print(f"Player: {username}")
        print(f"Pokemons: {', '.join(user_team)}")
    else:
        print(f"Player: {username}")
        print(f"Pokemons: Not found")

    return player_teams.get(user_player_id, [])


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
            player_id = parts[2][:2]  # Get the main player ID ('p1' or 'p2')
            pokemon_name = parts[3].split(",")[0]
            if pokemon_name not in battle_data["players"][player_id]["team"]:
                battle_data["players"][player_id]["team"].append(pokemon_name)

        # Turn-based actions
        elif action == "turn":
            turn_number = int(parts[2])
            battle_data["turns"].append({"turn": turn_number, "actions": []})

        # Actions within turns
        elif action in ["move", "faint", "-ability", "-item", "-damage", "-heal", "-status"]:
            if battle_data["turns"]:
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
