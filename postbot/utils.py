import discord
from datetime import datetime

from .api import CanadaPostPackage, ValidationError


def log(message):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}")


async def send_embed(client, channel_id, description, color, timestamp=None, author=None):
    embed = discord.Embed(
        description=description,
        color=color
    )

    if author is not None:
        embed.set_author(name=author)

    if timestamp is not None:
        embed.timestamp = timestamp

    await client.get_channel(channel_id).send(embed=embed)


async def refresh_tracking_events(database, client, channel_id, tracking_number):
    author = None
    db_events = database.get_events(channel_id)

    # setup our vars
    try:
        canada_post_package = CanadaPostPackage(tracking_number)
        events = canada_post_package.get_package_info()[::-1]
    except ValidationError:
        await send_embed(client, channel_id, "The tracking number provided was invalid.", 0xF71E1E, author="ValidationError")
        return

    to_remove = []

    # get the items that already exist in the db based on their time
    for db_event in db_events:
        for idx, event in enumerate(events):
            date_time_str = db_events[db_event]['time'].strftime('%Y-%m-%d %H:%M:%S')
            if date_time_str == f"{event['date']} {event['time']}":
                to_remove.append([event, idx])

    # give each canada post api event an index
    for idx, event in enumerate(events):
        events[idx] = [event, idx]

    # create a list with the items that aren't inside of the database
    not_in_database = [item for item in events if item not in to_remove]

    # if the not_in_database length is greater than 0, update it
    if len(not_in_database) > 0:
        for event in not_in_database:
            date_time_obj = datetime.strptime(f"{event[0]['date']} {event[0]['time']}", '%Y-%m-%d %H:%M:%S')

            # get the previous items id

            database.insert_event(tracking_number, channel_id, {str(event[1]): {
                "description": event[0]['descriptions']['descEn'],
                "time": date_time_obj
            }})

            try:
                country = event[0]['location']['countryNmEn']
            except KeyError:
                country = None

            if country is not None:
                author = f"{event[0]['location']['city']}, {event[0]['location']['regionCd']}, {country}"

            log(f"[{tracking_number}] inserted {tracking_number, event[0]['descriptions']['descEn'], date_time_obj}")
            await send_embed(client, channel_id, event[0]['descriptions']['descEn'], 0x7CDB2E, date_time_obj, author)
    else:
        log(f"[{tracking_number}] no update needed\n")
