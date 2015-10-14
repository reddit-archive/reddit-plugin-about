import sys
import ConfigParser


def main(config_file):
    parser = ConfigParser.RawConfigParser()
    with open(config_file, "r") as cf:
        parser.readfp(cf)
    print >> sys.stderr, "I'm a plugin script"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "USAGE: %s /path/to/config-file.ini" % sys.argv[0]
        sys.exit(1)

    main(sys.argv[1])
