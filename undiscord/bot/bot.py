# -*- coding: utf-8 -*-

"""discord bot definition"""

import json
import re
from logging import getLogger

from discord import Server, Channel, Message, Member
from discord.ext import commands
from discord.errors import Forbidden, HTTPException, NotFound

__log__ = getLogger(__name__)

BOT = commands.Bot(command_prefix="un>", self_bot=True)


def slugify(value):
    """Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value)
    value = re.sub('[^\w\s-]', '', value).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value


@BOT.event
async def on_ready():
    """Startup logged callout/setup"""
    __log__.info("logged in as: {}".format(BOT.user.id))

    # get server
    for server in BOT.servers:
        with open("{}_messages.json".format(slugify(server.name)), 'w+') as f:
            server: Server = server
            __log__.info("scraping server: name: {} id: {}".format(server.name, server.id))
            server_data = {
                "name": server.name,
                "id": server.id,
                "channels": []
            }
            # get channel
            for channel in server.channels:
                channel: Channel = channel
                __log__.info("scraping channel: name: {} id: {}".format(channel.name, channel.id))
                channel_data = {
                    "name": channel.name,
                    "id": channel.id,
                    "messages": []
                }

                try:
                    async for message in BOT.logs_from(channel, limit=500):
                        message: Message = message
                        __log__.info("obtained message: author: {} content: {}".format(message.author.id, message.content))
                        author: Member = message.author
                        message_data = {
                            "author": {
                                "name": author.name,
                                "id": author.id
                            },
                            "server": message.server.name,
                            "channel": message.channel.name,
                            "timestamp": str(message.timestamp),
                            "content": message.content,
                            "mentions": [
                                dict(name=mentioned_member.name, id=mentioned_member.id)
                                for mentioned_member in message.mentions
                            ]
                        }
                        channel_data["messages"].append(message_data)
                        __log__.debug("parsed message: {}".format(message_data))
                except Forbidden:  # cant access channel
                    pass
                except NotFound:  # cant find channel
                    pass
                except HTTPException:
                    # TODO: maybe retry later
                    pass
                __log__.debug("parsed channel: {}".format(channel_data))
                server_data["channels"].append(channel_data)
            __log__.debug("parsed server: {}".format(server_data))
            json.dump(server_data, f)
    BOT.close()
