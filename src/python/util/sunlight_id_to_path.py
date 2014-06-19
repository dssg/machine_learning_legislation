#!/usr/bin/env python
# encoding: utf-8


import sys
import os

ROOT_DIR="/mnt/data/sunlight/bills_old_sunlight/"

def sunlightid_to_path(sunlight_id):
    bill_number, congress, version = sunlight_id.split('-')
    return "%s%s-%s/%s/%s" %(ROOT_DIR, bill_number, congress, version, sunlight_id)

if __name__ == '__main__':
    sunlightid_to_path(sys.argv[1])

