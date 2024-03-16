from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from aiolimiter import AsyncLimiter
import httpx
import pokemodel

app = FastAPI()

# Define an AsyncLimiter with a rate of 10 requests per second (10/1).
limiter = AsyncLimiter(10, 1)

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
    # Wait for the rate limiter before proceeding.
    await limiter.acquire()
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            # It's a good practice to handle errors such as rate limits from the external API as well.
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return None


async def fetch_ladder(formatName: str):
    # Wait for the rate limiter before proceeding.
    await limiter.acquire()
    url = f"https://pokemonshowdown.com/ladder/{formatName}.json"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            # It's a good practice to handle errors such as rate limits from the external API as well.
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return None


async def fetch_match_history(player: str):
    # Wait for the rate limiter before proceeding.
    await limiter.acquire()
    url = f"https://replay.pokemonshowdown.com/search.json?user={player}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            # It's a good practice to handle errors such as rate limits from the external API as well.
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return None


async def fetch_replay(matchID: str):
    # Wait for the rate limiter before proceeding.
    await limiter.acquire()
    url = f"https://replay.pokemonshowdown.com/{matchID}.log"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.text  # Return the raw text response instead of trying to parse JSON
        else:
            # It's a good practice to handle errors such as rate limits from the external API as well.
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            return None
