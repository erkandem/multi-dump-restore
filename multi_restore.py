from  collections import namedtuple
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime as dt
import multiprocessing
import appconfig as ac

PAUSE_BETWEEN_RESTORE_SECONDS = 1
CORES = multiprocessing.cpu_count()

LogDetails = namedtuple(
    'LogDetails',
    ['k', 'K', 'schema', 'source', 'target']
)


def nowstr():
    """enforce standardized dt string format"""
    return dt.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def restore_loop(
        pgc: ac.PostgresConfig,
        db_obj: {str: {'str': Path}},
        *,
        source: str,
        target: str,
        armed: bool
):
    schemata = db_obj['schemata']
    bkp_name = db_obj['bkp_name']
    K = len(schemata)
    for k, schema in enumerate(schemata):
        file_path = schemata[schema]['path']
        cmd_fragments = [
            f'{pgc.pg_restore_path}',
            '--dbname', f'{target}',
            '--host', f'\'{pgc.host}\'',
            '--port', f'\'{pgc.port}\'',
            '--username', f'\'{pgc.user}\'',
            '--no-password',
            '--verbose',
            '--jobs', f"{int(CORES)} ",
            f'\'{file_path}\'',
            '>>', f'logs/{bkp_name}_multi_restore.log', '2>&1',
        ]

        details = LogDetails(k, K, schema, source, target)
        execute_restore(cmd_fragments, armed=armed, d=details)


def execute_restore(cmd_fragments, *, armed=False, d: LogDetails = None):
    if d is None:
        d = LogDetails(0, 0, 0, 0, 0)
    cmd = ' '.join(cmd_fragments)
    if not armed:
        print(cmd)
    else:
        print(
            json.dumps({
                'dt': nowstr(),
                'progress': f'{d.k + 1}/{d.K}',
                'msg': f'restoring {d.schema} from {d.source} to {d.target}'
            })
        )
        os.system(cmd)
        print(
            json.dumps({
                'dt': nowstr(),
                'progress': f'{d.k + 1}/{d.K}',
                'msg': f'restored {d.schema} from {d.source} to {d.target}'
            })
        )


def restore_scouting(single_backup_path: Path):
    """
    Creates a representation of the `backup_path` folder
    and sub folders

    Args:
    backup_path: absolute path to the directory
                in which pg_dump output was directed
    """
    db_folders = {
        db.name: {
            'name': db.name,
            'bkp_name': single_backup_path.name,
            'path': db.__str__(),
            'schemata': {
                sm.stem: {
                    'name': sm.stem,
                    'path': sm.__str__()
                } for sm in db.iterdir() if sm.suffix == '.backup'
            }
        }
        for db in single_backup_path.iterdir() if db.is_dir()
    }
    return db_folders


def main(args: argparse.Namespace):
    if sys.platform != 'linux':
        raise NotImplementedError('script is only configured to work on linux')
    Path('logs').mkdir(exist_ok=True, parents=True)
    bkp_base_path = Path(args.bkp_base_path)
    bkp_path = bkp_base_path / args.backup_name
    if not bkp_path.exists():
        raise ValueError(f'Path does not seem to exist\n: {bkp_path}')
    ini = restore_scouting(bkp_path)
    if args.backup_db_name in list(ini):
        N = len(ini[args.backup_db_name]['schemata'])
        print(f'# starting to restore {N} schemata')
        restore_loop(
            ac.pgc,
            ini[args.backup_db_name],
            source=args.backup_db_name,
            target=args.restore_db_name,
            armed=args.armed
        )
    else:
        msg = f'{args.bkp_db_name} was not found at f{str(bkp_path)}'
        raise ValueError(msg)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        'backup_name',
        help='ONE PARTICULAR backup e.g. 20191123 for /home/user/db/bkp/20191123'
    )
    p.add_argument(
        'bkp_db_name',
        help='database from which the schema was dumped'
    )
    p.add_argument(
        'restore_db_name',
        help='database to which the schema should be restored to'
    )
    p.add_argument(
        '--bkp_base_path',
        help='path to all backups on system default: /home/user/db/bkp/',
        default=str(ac.BKP_BASE_PATH),
    )
    p.add_argument(
        '--armed',
        help='really execute commands? `False` by default',
        default='False',
        choices=['True', 'False']
    )
    a = p.parse_args()
    if a.armed == 'False':
        a.armed = False
    if a.armed == 'True':
        a.armed = True
    ac.check_if_known_db_name(a.backup_db_name)
    ac.check_if_known_db_name(a.restore_db_name)
    main(a)
