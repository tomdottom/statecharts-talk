#!/usr/bin/env python
from __future__ import print_function

import sys

import sismic.io as sio

if __name__ == "__main__":
    input_path = sys.argv[1]
    chart = sio.import_from_yaml(filepath=input_path)
    print(sio.export_to_plantuml(chart))
