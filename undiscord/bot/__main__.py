#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for undiscord Discord bot"""

import argparse
import asyncio
import sys
from logging import getLogger

from discord import Client, Server, Channel, Message, Member, Forbidden, \
    NotFound, HTTPException
from pony.orm import Database, Required, db_session, Set, Optional, PrimaryKey

from undiscord.common import add_log_parser, init_logging
from undiscord.friend_map import FriendMap, PlotlyAdapter

__log__ = getLogger(__name__)

DEFAULT_MESSAGES_NUMBER: int = 30
DEFAULT_TIMEOUT: float = 30.0

db = Database()


class Member(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    messages = Set("Message")


class Server(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    channels = Set("Channel")


class Channel(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    server = Required(Server)
    messages = Set("Message")


class Message(db.Entity):
    author = Required(Member)
    content = Optional(str)
    timestamp = Required(str)
    channel = Optional(Channel)


db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for undiscord Discord bot"""
    parser = argparse.ArgumentParser(
        description="Start the UnDiscord Discord bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-o", "--output-file", dest="output_file",
                        required=True,
                        help="Path to output the Discord server member "
                             "network graph")
    parser.add_argument("-tf", "--token-file", dest="token_file",
                        required=True,
                        help="Path to file containing the Discord token for "
                             "the bot")
    parser.add_argument("-s", "--server-name", dest="server_name",
                        required=True,
                        help="Name of the Discord server to collect "
                             "messages from")
    parser.add_argument("-n", "--message-number", type=int,
                        dest="message_number",
                        default=DEFAULT_MESSAGES_NUMBER,
                        help="Number of Discord messages to collect")
    parser.add_argument("-t", "--timeout", type=float,
                        default=DEFAULT_TIMEOUT,
                        help="Time to collect Discord messages before "
                             "stopping")

    add_log_parser(parser)

    return parser


def main(argv=sys.argv[1:]) -> int:
    """main entry point undiscord Discord bot"""
    parser = get_parser()

    args = parser.parse_args(argv)
    init_logging(args, "undiscord_bot.log")
    with open(args.token_file, "r") as f:
        token = f.read().strip()

    server_data = scrape_server(
        token=token,
        server_name=args.server_name,
        messages_number=args.message_number,
        timeout=args.timeout
    )

    friend_map = FriendMap(server_data)
    html_graph = PlotlyAdapter(friend_map, "reingold")
    html_graph.plot_graph(args.output_file)

    return 0


@db_session
def scrape_server(token: str,
                  server_name: str,
                  messages_number: int = DEFAULT_MESSAGES_NUMBER,
                  timeout: float = DEFAULT_TIMEOUT):
    loop = asyncio.new_event_loop()
    client = Client(is_bot=False, loop=loop, max_messages=messages_number)
    server_data = {}

    @client.event
    async def on_ready():
        __log__.info("logged in as: {}".format(client.user.id))

        for server in client.servers:
            if server.name != server_name:
                continue
            server: Server = server
            __log__.info("obtained server: name: {} id: {}".format(
                server.name, server.id))
            server_data.update(
                {
                    "name": server.name,
                    "id": server.id,
                    "channels": []
                }
            )
            ser = Server(name=server.name, id=server.id)

            for channel in server.channels:
                channel: Channel = channel
                __log__.info("obtained channel: name: {} id: {}".format(
                    channel.name, channel.id))
                channel_data = {
                    "name": channel.name,
                    "id": channel.id,
                    "messages": []
                }
                chan = Channel(name=channel.name, id=channel.id, server=ser)
                try:
                    async for message in client.logs_from(channel,
                                                          limit=messages_number):
                        message: Message = message
                        __log__.info(
                            "obtained message: author: {} content: {}".format(
                                message.author.id, message.content))
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
                                dict(
                                    name=mentioned_member.name,
                                    id=mentioned_member.id
                                )
                                for mentioned_member in message.mentions
                            ]
                        }
                        mem = Member.get(id=author.id)
                        if mem is None:
                            mem = Member(
                                id=author.id,
                                name=author.name,
                            )
                        Message(
                            author=mem,
                            content=message.content,
                            timestamp=str(message.timestamp),
                            channel=chan,
                        )
                        channel_data["messages"].append(message_data)
                except Forbidden:  # cant access channel
                    pass
                except NotFound:  # cant find channel
                    pass
                except HTTPException:  # discord likely down
                    pass
                server_data["channels"].append(channel_data)
        client.close()

    loop.run_until_complete(client.login(token, bot=False))
    try:
        loop.run_until_complete(
            asyncio.wait_for(client.connect(), timeout, loop=loop))
    except asyncio.TimeoutError:
        pass
    loop.run_until_complete(client.logout())
    loop.close()
    return server_data


if __name__ == "__main__":
    sys.exit(main())
