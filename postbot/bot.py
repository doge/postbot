from config import config
import discord
from discord.ext import commands, tasks

from .db import Database
from .utils import log, refresh_tracking_events

database = Database(config['ip'], config['port'], config['database_name'], config['collection_name'])
client = commands.Bot(command_prefix=config['command_prefix'])


@tasks.loop(minutes=config['daemon_timeout'])
async def package_daemon():
    # for every tracking number inside of the database
    for pair in database.get_tracking_numbers():
        log(f"[package daemon] refreshing tracking events for channel id {pair['_id']['channelId']}")
        await refresh_tracking_events(database, client, pair['_id']['channelId'], pair['_id']['trackingNumber'])
    log(f"[package daemon] refreshing in {config['daemon_timeout']} minutes...\n")


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"packages | $track"))

    log("Bot fully initialized.\n")

    log("Starting package daemon...")
    package_daemon.start()
    log("Package daemon started.\n")


@client.command()
async def track(ctx, tracking_number):
    print(tracking_number)
    await refresh_tracking_events(database, client, ctx.message.channel.id, tracking_number)

