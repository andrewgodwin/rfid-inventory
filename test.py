import time
from ru5102 import Reader, commands

reader = Reader("COM6")

seen_tags = set()

print(reader.run(commands.GetReaderInformation()))

print("")

while True:
    response = reader.run(commands.Inventory())
    print(response)
    seen_tags.update(response.tags)
    print("Seen: %i tags" % (len(seen_tags)))
    time.sleep(1)
