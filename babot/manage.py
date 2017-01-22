import argparse

from models import (
    engine,
    Base
)

CREATE_ALL = 'create_all'
DROP_ALL = 'drop_all'

CHOICES = [
    CREATE_ALL,
    DROP_ALL
]

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'command', type=str, choices=CHOICES, help='Command to be executed')
    return parser.parse_args()

def main():
    args = parse()
    if args.command == CREATE_ALL:
        Base.metadata.create_all(engine)
    elif args.command == DROP_ALL:
        Base.metadata.drop_all(engine)

if __name__ == '__main__':
    main()
