#!/usr/bin/env python
# encoding: utf-8

import sys
import os
import re


def main(file_path):
    pattern = r'\*+\[+([\w ]+)\]+'
    for match in re.findall(pattern, open(file_path).read() ):
        print match


if __name__ == '__main__':
    main(sys.argv[1])

