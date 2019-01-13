#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for undiscord discord bot"""

import argparse
import asyncio
import sys
from logging import getLogger

from discord import Client, Server, Channel, Message, Member, Forbidden, \
    NotFound, HTTPException

from undiscord.common import add_log_parser, init_logging

__log__ = getLogger(__name__)

DEFAULT_MESSAGES_NUMBER: int = 30
DEFAULT_TIMEOUT: float = 30.0


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for undiscord discord bot"""
    parser = argparse.ArgumentParser(
        description="Start the UnDiscord Discord bot",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("-s", "--server-name", type=str, required=True,
                        dest="server_name",
                        help="Name of the Discord server to collect "
                             "messages from")
    parser.add_argument("-n", "--message-number", type=int,
                        default=DEFAULT_MESSAGES_NUMBER,
                        dest="message_number",
                        help="Number of Discord messages to collect")
    parser.add_argument("-t", "--timeout", type=float,
                        default=DEFAULT_TIMEOUT,
                        help="Time to collect Discord messages before "
                             "stopping")
    parser.add_argument("-tf", "--token-file", type=str, dest="token_file",
                        required=True,
                        help="Path to file containing the Discord token for "
                             "the bot")

    add_log_parser(parser)

    return parser


def main(argv=sys.argv[1:]) -> int:
    """main entry point undiscord discord bot"""
    parser = get_parser()

    args = parser.parse_args(argv)
    init_logging(args, "undiscord_bot.log")
    with open(args.token_file, "r") as f:
        token = f.read().strip()
    scrape_server(token, args.server_name, args.message_number, args.timeout)
    return 0


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
            __log__.info(
                "scraping server: name: {} id: {}".format(server.name,
                                                          server.id))
            server_data.update({
                "name": server.name,
                "id": server.id,
                "channels": []
            })
            # get channel
            for channel in server.channels:
                channel: Channel = channel
                __log__.info("scraping channel: name: {} id: {}".format(
                    channel.name, channel.id))
                channel_data = {
                    "name": channel.name,
                    "id": channel.id,
                    "messages": []
                }

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
                                dict(name=mentioned_member.name,
                                     id=mentioned_member.id)
                                for mentioned_member in message.mentions
                            ]
                        }
                        channel_data["messages"].append(message_data)
                        __log__.debug(
                            "parsed message: {}".format(message_data))
                except Forbidden:  # cant access channel
                    pass
                except NotFound:  # cant find channel
                    pass
                except HTTPException:
                    pass
                __log__.debug("parsed channel: {}".format(channel_data))
                server_data["channels"].append(channel_data)
            __log__.debug("parsed server: {}".format(server_data))

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
