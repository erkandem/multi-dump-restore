import sys
import subprocess


def main():
    """
    access both scripts from `mdr`
    pattern copied from flask script and flask.cli
    """
    if sys.argv[1] == 'dump':
        args = ['python', 'multi_dump.py'] + sys.argv[2:]
    elif sys.argv[1] == 'restore':
        args = ['python', 'multi_restore.py'] + sys.argv[2:]
    else:
        msg = f'expected `dump or `restore` as first argument. got {sys.argv[1]}'
        raise ValueError(msg)
    subprocess.run(args)


if __name__ == '__main__':
    main()
