#########
undiscord
#########

.. image:: https://travis-ci.com/nklapste/undiscord.svg?token=PXHp9tdymHUxZDzfWpfK&branch=master
    :target: https://travis-ci.com/nklapste/undiscord
    :alt: Build Status

.. image:: https://codecov.io/gh/nklapste/undiscord/branch/master/graph/badge.svg?token=Toda5ZCZ9a
    :target: https://codecov.io/gh/nklapste/undiscord
    :alt: Coverage Status

A Discord bot and server for the 2019 Hackathon.

Overview
========

undiscord is a python Discord bot and server that generates network map
graphs from the conversations between Members in a Discord server. This
allows one to gain inferences on the subgroups and behaviours of members
within the Discord Server.

Installation
============

undiscord can be installed from source by running:

.. code-block:: bash

    pip install .

Within the same directory as undiscord's ``setup.py`` file.


Usage
=====

After installing undiscord help on using the Discord Bot component
``undiscord-bot`` can be obtained by running the following command:

.. code-block:: bash

    undiscord-bot --help

Additionally, help on using the server component ``undiscord-server`` can be
obtained by running the following command:

.. code-block:: bash

    undiscord-server --help
