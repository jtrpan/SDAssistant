import asyncio
import csv

from pokemon import Pokemon, Team
from main import fetch_ladder, fetch_match_history, fetch_replay, fetch_pokemon_data

selected_format = 'gen3ou'


def define_format(formatName):
    gen_number = formatName[3]
    format_type = "OU" if formatName[4:].lower() == 'ou' else formatName[4:].upper()
    return f"[Gen {gen_number}] {format_type}"


def is_new_format(formatName):
    gen_number = int(formatName[3])
    if gen_number >= 5:
        return True
    return False


def extract_players(data):
    return [player.get('username') for player in data.get('toplist', []) if player.get('username')]


def extract_ids(data, desired_format):
    return [item['id'] for item in data if item['format'] == desired_format]


def extract_pokemon_by_username(game_log, username):
    lines = game_log.split("\n")
    player_number = ""
    if is_new_format(selected_format):
        for line in lines:
            if f"|player|p1|{username}" in line or f"|player|p2|{username}" in line:
                player_number = line.split("|")[2]
                break
        return [line.split("|")[3].split(",")[0] for line in lines if line.startswith(f"|poke|{player_number}|")]
    else:
        pokemon_set = set()

        # Determine player number based on username
        for line in lines:
            if f"|player|p1|{username}" in line:
                player_number = "p1"
                break
            elif f"|player|p2|{username}" in line:
                player_number = "p2"
                break

        # Track all unique Pokémon switched in by the player
        for line in lines:
            if line.startswith(f"|switch|{player_number}") or line.startswith(f"|drag|{player_number}"):
                pokemon_info = line.split("|")[3]
                pokemon_name = pokemon_info.split(",")[0]  # Remove any form or gender information
                pokemon_set.add(pokemon_name)

        return list(pokemon_set)


async def fetch_game_data(match_ids, username, max_attempts=10):
    for match_id in match_ids[:max_attempts]:
        game_log = await fetch_replay(match_id)
        if game_log:
            # print(game_log)
            team_details = extract_pokemon_details(game_log, username)

            # Now, we create Pokemon instances with the detailed information.
            pokemons = [
                Pokemon(
                    name=pkmn['name'],
                    ability=pkmn.get('ability', 'Unknown'),  # Provide a default value if 'ability' key is missing
                    item=pkmn.get('item', 'None'),  # Provide a default value if 'item' key is missing
                    moveset=pkmn['moveset']
                ) for pkmn in team_details
            ]

            # Create the Team instance with the detailed Pokémon.
            team = Team(username, pokemons)
            return team
    return None


def extract_pokemon_details(game_log, username):
    details = {}
    current_player = ""
    seen_pokemon = set()

    for line in game_log.split("\n"):
        if "|player|" in line and username in line:
            current_player = "p1" if "p1" in line else "p2"
            break  # Identify the player once and stop checking

    for line in game_log.split("\n"):
        parts = line.split("|")
        action = parts[1] if len(parts) > 1 else ""
        player = parts[2] if len(parts) > 2 else ""

        if player != current_player:
            continue  # Skip lines not related to the specified player

        if action in ["switch", "drag"]:
            pokemon_name = parts[3].split(",")[0]
            if pokemon_name not in details and len(details) < 6:
                # Initialize the Pokémon's data structure if not already present and ensure team does not exceed 6 Pokémon
                details[pokemon_name] = {'moveset': set(), 'ability': 'Unknown', 'item': 'None'}
            seen_pokemon.add(pokemon_name)  # Track seen Pokémon to correctly associate subsequent details

        elif action == "move":
            move_name = parts[3]
            if move_name != "Struggle" and seen_pokemon:
                # Exclude "Struggle" and ensure moves are added only if a Pokémon is currently tracked
                last_seen_pokemon = next(reversed(seen_pokemon))  # Get the last seen Pokémon to assign the move
                details[last_seen_pokemon]['moveset'].add(move_name)

        elif action == "-ability":
            ability = parts[4]
            if seen_pokemon:
                last_seen_pokemon = next(reversed(seen_pokemon))
                details[last_seen_pokemon]['ability'] = ability

        elif action == "-item":
            item = parts[4]
            if seen_pokemon:
                last_seen_pokemon = next(reversed(seen_pokemon))
                details[last_seen_pokemon]['item'] = item

    # Convert details to the required list format and ensure movesets are lists
    team_details = [{
        'name': pokemon,
        'ability': details[pokemon]['ability'],
        'item': details[pokemon]['item'],
        'moveset': list(details[pokemon]['moveset'])
    } for pokemon in details]

    return team_details


async def main():
    print("Fetching top players for the format: " + selected_format)
    ladder_data = await fetch_ladder(selected_format)
    players = extract_players(ladder_data)

    all_teams = []

    for player in players:  # Reduced for simplicity
        print(f"Processing player: {player}")
        user_data = await fetch_match_history(player)
        matches = extract_ids(user_data, define_format(selected_format))

        team = await fetch_game_data(matches, player, 10)
        if team:
            all_teams.append(team)
            print(team)  # Display the team

    # Write to CSV
    # try:
    #     with open('pokemon_teams.csv', 'w', newline='') as file:
    #         writer = csv.writer(file)
    #         for team in all_teams:
    #             writer.writerow(team)
    # except Exception as e:
    #     print(e)


if __name__ == "__main__":
    print("============ STARTING DATA COLLECTION ============")
    asyncio.run(main())
    print("============ FINISHING DATA COLLECTION ============")
    exit()
