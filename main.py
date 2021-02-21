from fpl import FPL
import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import aiohttp

load_dotenv()
TOKEN = os.getenv('TOKEN')

async def get_current_gameweek(fpl_session):
    gameweek_data = await fpl_session.get_gameweeks(return_json=True)
    for gameweek in gameweek_data:
        if gameweek['is_current']:
            return gameweek['id']

async def get_team_details(fpl_session, picks):
    string = "```"
    point_sum = 0
    for player in picks:
        if player['multiplier'] > 0:
            p = await fpl_session.get_player(player['element'])
            points = p.event_points * player['multiplier']
            point_sum += points 
            name = p.web_name
            if player['is_captain']:
                name += ' (C)'
            elif player['is_vice_captain']:
                name += ' (VC)'
            string += f'{name}: {points} \n'
    string += 'Bench:\n'
    for player in picks:
        if player['multiplier'] == 0:
            p = await fpl_session.get_player(player['element'])
            points = p.event_points * player['multiplier']
            name = p.web_name
            string += f'{name}: {points} \n'
    string += f"Total Points: {point_sum}```"
    return string

bot = commands.Bot(command_prefix='-')

@bot.event
async def on_ready():
    print("Logged In")


@bot.command(name='get_team')
async def get_player_team(ctx, player_id: int):
    async with aiohttp.ClientSession() as session:
        fpl = FPL(session)
        gameweek = await get_current_gameweek(fpl)
        await ctx.send(f'Got Gameweek: {gameweek}')
        user = await fpl.get_user(player_id)
        await ctx.send(f'Got {user}')
        picks = await user.get_picks(gameweek)
        team = await get_team_details(fpl, picks[gameweek])
    await ctx.send(team)

bot.run(TOKEN)