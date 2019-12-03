import time
from ru5102 import Reader, commands

reader = Reader("COM6")

seen_tags = set()

print(reader.run(commands.GetReaderInformation()))

print("")

while True:
    response = reader.run(commands.Inventory())
    seen_tags.update(response.tags)
    print("\rSeen: %i tags" % (len(seen_tags)), end="", flush=True)
