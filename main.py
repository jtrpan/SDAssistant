from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import httpx

import pokemodel

app = FastAPI()

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


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


async def fetch_ladder(formatName: str):
    url = f"https://pokemonshowdown.com/ladder/{formatName}.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None


async def fetch_match_history(player: str):
    url = f"https://replay.pokemonshowdown.com/search.json?user={player}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None


async def fetch_replay(matchID: str):
    url = f"https://replay.pokemonshowdown.com/{matchID}.log"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text  # Return the raw text response instead of trying to parse JSON
        else:
            return None
