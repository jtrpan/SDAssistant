class Pokemon:
    def __init__(self, name, ability=None, item=None, moveset=None):
        self.name = name
        self.ability = ability
        self.item = item
        self.moveset = moveset or []  # Ensuring moveset is a list

    def __str__(self):
        return f"{self.name} | Ability: {self.ability}, Item: {self.item}, Moveset: {', '.join(self.moveset)}"

class Team:
    def __init__(self, player, pokemons=[]):
        self.player = player
        self.pokemons = pokemons

    def add_pokemon(self, pokemon):
        self.pokemons.append(pokemon)

    def __str__(self):
        pokemons_str = "\n".join([str(pokemon) for pokemon in self.pokemons])
        return f"Player: {self.player}\nPokemons:\n{pokemons_str}"
