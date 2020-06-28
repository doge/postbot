from config import config
from discord import LoginFailure
from postbot.bot import client

try:
    client.run(config['bot_token'])
except LoginFailure as e:
    print(e)
