#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import argparse
import Manager

def sync():
    parser = argparse.ArgumentParser(description="synchronize Docker containers")
    
    parser.add_argument(
        "-n", "--no-pull",
        dest="pull",
        action="store_false",
        help="don't pull images",
    )
    
    parser.add_argument(
        "-i", "--allow-insecure-url",
        dest="insecure_registry",
        action="store_true", 
        help="allow pulling from non-ssl repositories",
    )
    
    parser.add_argument(
        "-s", "--remove-delay",
        dest="remove_delay",
        default=None,
        type=int,
        help="delay between stopping container and removing",
    )
    
    parser.add_argument(
        "config_dir",
        help="directory containing yaml config files",
    )
    
    parsed_args = parser.parse_args()
    
    Manager.main(
        parsed_args.config_dir,
        pull=parsed_args.pull,
        insecure_registry=parsed_args.insecure_registry,
        remove_delay=parsed_args.remove_delay,
    )

def gen():
    pass

if __name__ == "__main__":
    sync()
