# -*- coding: utf-8 -*-

"""determine whether a consequtive discord message is a reply to the message
before it"""

from logging import getLogger
from typing import List, Dict, Any, Generator

import pendulum

__log__ = getLogger(__name__)

REPLY_TIME = 20

Channel = Dict[str, Any]
Message = Dict[str, Any]


def get_connections_from_server(server_data: Message):
    for channel in server_data["channels"]:
        yield from get_possible_connections_from_channel(channel)
        yield from get_at_connections(channel)


def get_at_connections(channel: Channel):
    for message in channel["messages"]:
        if not message['mentions']:
            continue
        for mention in message['mentions']:
            yield message["author"]["name"], mention['name']


def get_possible_connections_from_channel(channel: Channel):
    channel_messages = channel["messages"]
    for i in range(len(channel_messages)):
        message = channel_messages[i]
        next_messages = channel_messages[i + 1:]
        for reply_message in get_message_replies(message, next_messages):
            yield message["author"]["name"], reply_message["author"]["name"]


def get_message_replies(message, next_messages: List[Message]) -> Generator[
    Message, None, None]:
    for next_message in next_messages:
        if next_message["author"]["id"] == message["author"]["id"]:
            break
        if pendulum.parse(next_message["timestamp"]).diff(
                pendulum.parse(
                    message["timestamp"])).in_seconds() <= REPLY_TIME:
            yield next_message
        else:
            break
