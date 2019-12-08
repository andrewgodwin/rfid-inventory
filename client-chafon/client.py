import click
import json
import requests
import time
from chafon import Reader, commands


SEND_GAP = 1


@click.command()
@click.argument("serial_port")
@click.argument("url")
@click.argument("token")
def main(serial_port, url, token):
    """
    Main command loop
    """
    # Set things up
    reader = Reader(serial_port)
    synchronizer = Synchronizer(url, token)
    seen_tags = set()
    seen_tags_time = 0
    # Show debugging info
    print(reader.run(commands.GetReaderInformation()))
    # Main detection loop
    while True:
        time.sleep(0.1)
        response = reader.run(commands.Inventory())
        seen_tags.update(["epc:%s" % tag for tag in response.tags])
        # If it's been enough time, update the server with what happened
        if time.time() - seen_tags_time > SEND_GAP:
            synchronizer.sync(seen_tags)
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
