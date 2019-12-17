import asyncio
import click
import json
from aiohttp_requests import requests


@click.command()
@click.option("--port", default=8003, help="Port to bind to")
@click.option("--host", default="0.0.0.0", help="IP address to bind to")
@click.argument("url")
@click.argument("token")
def main(url, token, host, port):
    """
    Proxies Alien notifications to a Listkeeper server
    """
    server = AlienNotificationServer(url, token)
    server.serve(host, port)
    print("Closing")


class AlienNotificationServer:

    def __init__(self, url, token):
        self.url = url
        self.token = token

    def serve(self, host, port):
        self.running = True
        loop = asyncio.get_event_loop()
        server = loop.run_until_complete(asyncio.start_server(self.handle, host, port))
        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

    async def handle(self, reader, writer):
        # Read tags from reader
        print("Got reader connection")
        tags = set()
        while True:
            line = await reader.readline()
            if not line:
                break
            line = line.strip().decode("utf-8")
            if not line or line.startswith("#") or line == "\x00":
                continue
            tag = "epc:" + line.split(",", 1)[0].replace(" ", "").lower()
            print("Received %r" % tag)
            tags.add(tag)
        print("Reader disconnected")
        # Sync them up
        if tags:
            try:
                await requests.post(
                    "%s/api/device/sync/" % self.url,
                    data=json.dumps({"token": self.token, "tags": list(tags)}),
                )
            except:
                print("Connection error during sync")
            else:
                print("Synced %i tags" % len(tags))


if __name__ == "__main__":
    main()
