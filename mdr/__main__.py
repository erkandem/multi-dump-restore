import subprocess
import sys


def main():
    """
    access both scripts from `mdr`
    pattern copied from flask script and flask.cli
    """
    scripts = {'dump', 'restore'}
    help_string = "` `".join(scripts)
    if len(sys.argv) > 1:
        called_script = sys.argv[1]
    else:
        msg = f'expected one of `{help_string}`'
        print(msg)
        return
    if called_script not in scripts:
        msg = f'expected one of `{help_string}` as first argument. got {called_script}'
        print(msg)
        return
    if called_script == 'dump':
        args = ['python', 'mdr/multi_dump.py'] + sys.argv[2:]
        subprocess.run(args)
    if called_script == 'restore':
        args = ['python', 'mdr/multi_restore.py'] + sys.argv[2:]
        subprocess.run(args)


if __name__ == '__main__':
    main()
