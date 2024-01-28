from fastapi import FastAPI
from typing import List
import httpx

import pokemodel

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/team/suggestions/")
async def team_suggestions(team: List[str]):
    # Use ML model to suggest a Pokémon
    # Fetch data from PokéAPI for detailed suggestions
    suggestions = pokemodel.predict(team)
    detailed_suggestions = [await fetch_pokemon_data(pokemon) for pokemon in suggestions]
    return {"suggestions": detailed_suggestions}


async def fetch_pokemon_data(pokemon_name: str):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
