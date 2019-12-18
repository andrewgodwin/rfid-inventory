Chafon Client
=============

A client for Chafon-style readers (RU5102 is the most commonly seen variant).

Talks to the readers over serial, and then uploads appearances to a Listkeeper
instance for further tracking.

Usage::

    client.py /dev/ttyUSB0 http://url-of-server/ DEVICEKEYHERE

