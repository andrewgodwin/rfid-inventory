import asyncio
import click
import json
from aiohttp_requests import requests


@click.command()
@click.option("--port", default=8003, help="Port to bind to")
@click.option("--host", default="0.0.0.0", help="IP address to bind to")
@click.argument("url")
@click.argument("tokens", nargs=-1)
def main(url, tokens, host, port):
    """
    Proxies Alien notifications to a Listkeeper server
    """
    server = AlienNotificationServer(url, tokens)
    server.serve(host, port)
    print("Closing")


class AlienNotificationServer:

    def __init__(self, url, tokens):
        self.url = url
        self.tokens = tokens

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
        tags = {}
        while True:
            # Read a line, or exit if the connection closed
            line = await reader.readline()
            if not line:
                break
            # Decode the line, throw away comments or null bytes
            line = line.strip().decode("utf-8")
            if not line or line.startswith("#") or line.startswith("\x00") or line.lower() == "(no tags)":
                continue
            # Split it into components
            try:
                raw_tag, antenna, rssi, name = line.split(",")
            except ValueError:
                print("Bad line: %r" % line)
                continue
            tag = "epc:%s/%i" % (raw_tag.replace(" ", "").lower(), float(rssi))
            print("Received %r from %s, antenna %s" % (tag, name, antenna))
            tags.setdefault(int(antenna), set()).add(tag)
        print("Reader disconnected")
        # Sync them up
        if tags:
            token_values = {}
            for antenna, tag_values in tags.items():
                # See if we have a token for that antenna, or use default
                try:
                    token = self.tokens[antenna]
                except IndexError:
                    token = self.tokens[0]
                # Group by token
                token_values.setdefault(token, set()).update(tag_values)
            # Post results to the server by token
            for token, tag_values in token_values.items():
                try:
                    await requests.post(
                        "%s/api/device/sync/" % self.url,
                        data=json.dumps({"token": token, "tags": list(tag_values)}),
                    )
                except Exception as e:
                    print("Connection error during sync: %s" % e)
                else:
                    print("Synced %i tags" % len(tag_values))


if __name__ == "__main__":
    main()
