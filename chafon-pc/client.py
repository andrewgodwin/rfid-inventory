#!/usr/bin/env python3

import click
import json
import requests
import time
from chafon import Reader, commands


SEND_GAP_ACTIVE = 1
SEND_GAP_INACTIVE = 120


@click.command()
@click.option("--power", default=5)
@click.option("--reader-type", default="ru5102")
@click.argument("serial_port")
@click.argument("url")
@click.argument("token")
def main(serial_port, url, token, power, reader_type):
    """
    Main command loop
    """
    # Set things up
    reader = Reader(serial_port, type=reader_type)
    synchronizer = Synchronizer(url, token)
    seen_tags = set()
    last_seen_tags = seen_tags
    seen_tags_time = 0
    # Verify reader info
    reader_info = reader.run(commands.GetReaderInformation())
    assert reader_info.reader_type == reader_type, (
        "The reader is type %s, not configured type %s"
        % (reader_info.reader_type, reader_type)
    )
    # Set power
    reader.run(commands.SetPower(power))
    # Main detection loop
    while True:
        response = reader.run(commands.Inventory())
        seen_tags.update(["epc:%s" % tag for tag in response.tags])
        # If it's been enough time, update the server with what happened
        time_since_send = time.time() - seen_tags_time
        tags_changed = seen_tags != last_seen_tags
        if (
            tags_changed and time_since_send > SEND_GAP_ACTIVE
        ) or time_since_send > SEND_GAP_INACTIVE:
            synchronizer.sync(seen_tags)
            last_seen_tags = seen_tags
            seen_tags = set()
            seen_tags_time = time.time()


class Synchronizer:
    """
    Sends tags up to the server, and returns the current mode.
    """

    def __init__(self, url, token):
        self.url = url.rstrip("/")
        self.token = token

    def sync(self, tags):
        try:
            requests.post(
                "%s/api/device/sync/" % self.url,
                data=json.dumps({"token": self.token, "tags": list(tags)}),
            )
        except requests.exceptions.ConnectionError:
            click.echo("Server connection error, waiting...")
            time.sleep(3)
        else:
            print(".", end="", flush=True)


if __name__ == "__main__":
    main()
