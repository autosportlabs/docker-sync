#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import getopt
import sys
import Manager

def sync():
    def usage():
        print "Usage: %s -h | --help" % sys.argv[0]
        print "       %s -n | --no-pull" % sys.argv[0]

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hn", ["help", "no-pull"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    pull = True

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-n", "--no-pull"):
            pull = False
        else:
            assert False, "unhandled option"

    Manager.main(pull)

def gen():
    pass

if __name__ == "__main__":
    sync()
