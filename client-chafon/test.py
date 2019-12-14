#!/usr/bin/env python3

import sys
from chafon import Reader, commands


reader = Reader(sys.argv[1], type="rru2881")

reader.run(commands.SetPower(30))
print(reader.run(commands.GetReaderInformation()))

response = reader.run(commands.Inventory())
print(response.tags)
