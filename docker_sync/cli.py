#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import Manager

def sync():
    parser = argparse.ArgumentParser(description="synchronize Docker containers")
    parser.add_argument("-n", "--no-pull", dest="pull", action="store_false", help="don't pull images")
    parser.add_argument("config_dir", help="directory containing yaml config files")
    
    parsed_args = parser.parse_args()
    
    Manager.main(parsed_args.config_dir, pull=parsed_args.pull)

def gen():
    pass

if __name__ == "__main__":
    sync()
