#!/usr/bin/python
# -*- coding: utf-8 -*-

from json import loads

from undiscord.reply_pry import get_possible_connections_from_server

MOCK_SERVER_DATA = loads("""
{
  "name": "ex",
  "id": "00001",
  "channels": [
    {
      "name": "ex channel",
      "id": "00002",
      "messages": [
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:27:09.000000",
          "content": "msg 1",
          "mentions": []
        },
        {
          "author": {
            "name": "user 2",
            "id": "2"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:26:11.000000",
          "content": "msg 2",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:41.000000",
          "content": "msg 3",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:40.000000",
          "content": "msg 4",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:36.000000",
          "content": "msg 5",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:31.000000",
          "content": "msg 6",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:27.000000",
          "content": "msg 7",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:17.000000",
          "content": "msg 8",
          "mentions": []
        },
        {
          "author": {
            "name": "user 2",
            "id": "2"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:15.000000",
          "content": "msg 9",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:01.000000",
          "content": "msg 10",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:25:00.000000",
          "content": "msg 11",
          "mentions": []
        },
        {
          "author": {
            "name": "user 1",
            "id": "1"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:24:58.000000",
          "content": "msg 12",
          "mentions": []
        },
        {
          "author": {
            "name": "user 2",
            "id": "2"
          },
          "server": "ex server",
          "channel": "ex channel",
          "timestamp": "2018-11-11 11:24:45.000000",
          "content": "msg 13",
          "mentions": []
        }
      ]
    }
  ]
}
""")


def test_get_possible_connections_from_server():
    connection_tuples = get_possible_connections_from_server(MOCK_SERVER_DATA)
    assert [(a["author"]["name"], b["author"]["name"]) for a, b in
            connection_tuples] == [
               ('user 1', 'user 2'),
               ('user 2', 'user 1'),
               ('user 2', 'user 1'),
               ('user 2', 'user 1'),
               ('user 1', 'user 2')
           ]
