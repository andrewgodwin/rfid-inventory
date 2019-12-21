#!/usr/bin/env python3

import click
import json
import requests
import time
from chafon import Reader, commands, exceptions


TAG_PRESENCE_LENGTH = 1
SEND_GAP_ACTIVE = 2
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
    reader = Reader(serial_port, type=reader_type)
    synchronizer = Synchronizer(url, token)
    RFIDClient(reader, synchronizer, power).run()


class RFIDClient:
    """
    Represents the main loop of the client
    """

    def __init__(self, reader, synchronizer, power=None):
        self.reader = reader
        self.synchronizer = synchronizer
        self.power = power

    def run(self):
        # See if we need to set power
        if self.power:
            self.reader.run(commands.SetPower(self.power))
            print("Set reader power to %i" % self.power)
        # Initialise loop state
        self.last_sync_time = time.time()
        self.last_sent_tags = set()
        self.seen_tags = TagSet(expiry=TAG_PRESENCE_LENGTH)
        self.written_tags = set()
        # Start loop
        while True:
            # Write a tag if we need to
            if self.synchronizer.write:
                done = self.write_tag(self.synchronizer.write)
                if done:
                    self.synchronizer.write = None
            # Run the inventory
            self.inventory()
            # See if we need to sync
            if self.sync_required():
                self.sync()


    def inventory(self):
        """
        Inventories tags in the field and adds them to a list
        """
        response = self.reader.run(commands.Inventory())
        self.seen_tags.update(["epc:%s" % tag for tag in response.tags])

    def write_tag(self, tag):
        """
        Writes a tag if there's one to write
        """
        # Ensure the tag is correct
        if tag.startswith("epc:"):
            try:
                self.reader.run(commands.WriteEPC(tag[4:]))
            except (exceptions.NoTagError, exceptions.PoorCommunicationError):
                return False
            else:
                print("Wrote tag %r" % self.synchronizer.write)
                self.written_tags.add(self.synchronizer.write)
                return True
        else:
            print("Write error: Bad tag type in %r" % tag)
            # Return done so the bad tag is discarded
            return True

    def sync_required(self):
        """
        Returns if a sync is currently needed
        """
        time_since_sync = time.time() - self.last_sync_time
        if time_since_sync > SEND_GAP_INACTIVE:
            return True
        if time_since_sync > SEND_GAP_ACTIVE:
            if ((self.seen_tags.current() != self.last_sent_tags) or self.written_tags):
                return True
        return False

    def sync(self):
        """
        Runs a sync
        """
        self.last_sent_tags = self.seen_tags.current()
        self.synchronizer.sync(self.last_sent_tags, self.written_tags)
        self.written_tags = set()
        self.last_sync_time = time.time()


class TagSet:
    """
    Represents a set of tag objects and when they were seen.
    Expires tags out of the list after a certain number of seconds.
    """

    def __init__(self, expiry=1):
        self.expiry = expiry
        self.tags = {}

    def add(self, tag):
        self.tags[tag] = time.time()

    def update(self, tags):
        for tag in tags:
            self.add(tag)

    def current(self):
        result = set()
        for tag, seen in list(self.tags.items()):
            if time.time() - seen > self.expiry:
                del self.tags[tag]
            else:
                result.add(tag)
        return result

    def __iter__(self):
        return iter(self.current())


class Synchronizer:
    """
    Sends tags up to the server, and returns the current mode.
    """

    def __init__(self, url, token):
        self.url = url.rstrip("/")
        self.token = token
        self.write = None

    def sync(self, seen_tags, written_tags):
        try:
            response = requests.post(
                "%s/api/device/sync/" % self.url,
                data=json.dumps({"token": self.token, "tags": list(seen_tags), "written": list(written_tags)}),
            )
        except requests.exceptions.ConnectionError:
            click.echo("Server connection error, waiting...")
            time.sleep(3)
        else:
            response_data = response.json()
            if response_data.get("write"):
                self.write = response_data.get("write")
                print("Sent %i tags, queued write for %s" % (len(seen_tags), self.write))
            else:
                self.write = None
                print("Sent %i tags" % len(seen_tags))


if __name__ == "__main__":
    main()
