import requests
import mysql.connector

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )

# Function to fetch data from PokeAPI
def fetch_pokemon_data(pokemon_name):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data for {pokemon_name}")
        return None

# Function to populate the database
def populate_db(pokemon_name):
    data = fetch_pokemon_data(pokemon_name)
    if not data:
        return

    conn = connect_db()
    cursor = conn.cursor()

    # Insert data into Pokemon table
    pokemon_id = data['id']
    name = data['name']
    type1 = data['types'][0]['type']['name']
    type2 = data['types'][1]['type']['name'] if len(data['types']) > 1 else None
    base_experience = data['base_experience']

    cursor.execute("""
        INSERT INTO Pokemon (id, name, type1, type2, base_experience)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name=%s, type1=%s, type2=%s, base_experience=%s
    """, (pokemon_id, name, type1, type2, base_experience, name, type1, type2, base_experience))

    # Insert data into Moves table and link it to the Pokémon
    for move in data['moves']:
        move_name = move['move']['name']
        move_data = requests.get(move['move']['url']).json()
        move_id = move_data['id']
        power = move_data['power']
        pp = move_data['pp']
        accuracy = move_data['accuracy']

        cursor.execute("""
            INSERT INTO Moves (id, name, power, pp, accuracy)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            name=%s, power=%s, pp=%s, accuracy=%s
        """, (move_id, move_name, power, pp, accuracy, move_name, power, pp, accuracy))

        # Link the move to the Pokémon
        cursor.execute("""
            INSERT INTO Pokemon_Moves (pokemon_id, move_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            pokemon_id=%s, move_id=%s
        """, (pokemon_id, move_id, pokemon_id, move_id))

    # Commit the transaction
    conn.commit()

    # Close the connection
    cursor.close()
    conn.close()

# Main function to run the script
if __name__ == "__main__":
    pokemon_list = ["Tyranitar", "Pikachu", "Charizard"]  # Add more Pokémon as needed
    for pokemon in pokemon_list:
        populate_db(pokemon)
