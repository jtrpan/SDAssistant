import asyncio
import csv

from main import fetch_ladder, fetch_match_history, fetch_replay, fetch_pokemon_data

def define_format(formatName):
    gen_number = formatName[3]
    format_type = "OU" if formatName[4:].lower() == 'ou' else formatName[4:].upper()
    return f"[Gen {gen_number}] {format_type}"

def extract_players(data):
    return [player.get('username') for player in data.get('toplist', []) if player.get('username')]

def extract_ids(data, desired_format):
    return [item['id'] for item in data if item['format'] == desired_format]

def extract_pokemon_by_username(game_log, username):
    lines = game_log.split("\n")
    player_number = ""
    for line in lines:
        if f"|player|p1|{username}" in line or f"|player|p2|{username}" in line:
            player_number = line.split("|")[2]
            break
    return [line.split("|")[3].split(",")[0] for line in lines if line.startswith(f"|poke|{player_number}|")]

async def fetch_game_data(match_ids, username, max_attempts=10):
    for match_id in match_ids[:max_attempts]:
        game_log = await fetch_replay(match_id)
        if game_log:
            pkmn = extract_pokemon_by_username(game_log, username)
            if pkmn:
                return pkmn
    return []  # Return empty if no valid matches found within attempts

async def main():
    ladder_data = await fetch_ladder('gen9ou')
    print("cp1")
    players = extract_players(ladder_data)
    print("cp2")

    all_teams = []

    # Process a limited number of players to avoid overloading
    for player in players[:100]:
        print(player)
        user_data = await fetch_match_history(player)
        matches = extract_ids(user_data, define_format('gen9ou'))

        for match_id in matches[:5]:
            team = await fetch_game_data([match_id], player)
            if team:
                all_teams.append(team)

    print("cp3")

    # Write to CSV
    with open('pokemon_teams.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for team in all_teams:
            writer.writerow(team)


if __name__ == "__main__":
    print("starting test")
    asyncio.run(main())
    print("finished test")
    exit()