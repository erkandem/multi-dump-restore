import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime as dt
import multiprocessing
from appconfig import pgc, PostgresConfig, known_db_names

pause_var = 1   # length of pause  between loops
CORES = multiprocessing.cpu_count()


def nowstr():
    return dt.now().strftime('%Y-%m-%d %H:%M:%S')


def restore_loop(
        pgc: PostgresConfig,
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
        cmd = (
            f"{pgc.pg_restore_path} "
            f" --dbname {target} "
            f" --host '{pgc.host}' "
            f" --port '{pgc.port}' "
            f" --username '{pgc.user}' "
            f" --no-password "
            f" --jobs {int(CORES)} "
            f" '{file_path}' "
            f" >> logs/{bkp_name}_multi_restore.log 2>&1 "
        )
        if armed:
            print(
                json.dumps({
                    'dt': nowstr(),
                    'progress': f'{k+1}/{K}',
                    'msg': f'restoring {schema} from {source} to {target}'
                })
            )
            os.system(cmd)
            print(
                json.dumps({
                    'dt': nowstr(),
                    'progress': f'{k+1}/{K}',
                    'msg': f'restored {schema} from {source} to {target}'
                })
            )
        else:
            print(cmd)

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
    single_backup_path = Path(args.single_backup_path)
    if not single_backup_path.exists():
        raise ValueError(f'Path does not seem to exist\n: {single_backup_path}')
    ini = restore_scouting(single_backup_path)
    if args.backup_db_name in list(ini):
        N = len(ini[args.backup_db_name]['schemata'])
        print(f'# starting to restore {N} schemata')
        restore_loop(
            pgc,
            ini[args.backup_db_name],
            source=args.backup_db_name,
            target=args.restore_db_name,
            armed=args.armed
        )
    else:
        msg = f'{args.backup_db_name} was not found at f{single_backup_path.__str__()}'
        raise ValueError(msg)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        'single_backup_path',
        help='path to ONE PARTICULAR backup e.g. /home/user/db/bkp/20191123'
    )
    p.add_argument(
        'backup_db_name',
        help='database from which the schema was dropped'
    )
    p.add_argument(
        'restore_db_name',
        help='database to which the schema should be restored to'
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
    if a.backup_db_name not in known_db_names:
        print(
            f'The db_name given ({a.backup_db_name}) '
            f'does not appear in the known databases'
            f'Be sure you left a record in the .pgpass file'
        )
    if a.restore_db_name not in known_db_names:
        print(
            f'The db_name given ({a.restore_db_name}) '
            f'does not appear in the known databases'
            f'Be sure you left a record in the .pgpass file'
        )

    main(a)
