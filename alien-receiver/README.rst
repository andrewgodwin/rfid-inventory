Alien RFID Receiver
===================

A small Python program that acts as a Notify endpoint for Alien fixed RFID
readers, and forwards the received tags to a Listkeeper server.

Usage::

    receiver.py --port 8003 http://listkeeper-url antenna-0-token antenna-1-token

Multiple tokens can be provided, and they will be assigned to each antenna in
order. If there is an antenna without a matching token, it will use the token
for Antenna 0.

You will need to configure your reader with the following settings to
use this correctly::

    NotifyMode: ON
    NotfyAddress: 1.2.3.4:8003  (substitute the right IP here)
    NotifyFormat: Custom
    NotifyTrigger: Change
    TagListCustomFormat: %k,%a,%m,%N

We also recommend you set::

    NotifyTime: 300  (Allows a periodic resync of all tags in the field)
    NotifyRetryCount: -1  (Otherwise NotifyMode will turn itself off)
