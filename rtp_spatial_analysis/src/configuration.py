import argparse
from pathlib import Path

def add_run_args(parser, multiprocess=True):
    """
    Run command args
    """
    parser.add_argument('-c', '--configs_dir',
                        type=Path,
                        metavar='PATH',
                        default=Path(__file__).absolute().parent.parent.joinpath('configs'),
                        help='path to configs dir')


# Parse args at module level so they're available when imported
parser = argparse.ArgumentParser()
add_run_args(parser)
args, _ = parser.parse_known_args()


if __name__ == '__main__':
    print(f"configs_dir: {args.configs_dir}")
