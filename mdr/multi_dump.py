"""
shell piping
>>  append
>  create

pg dump formats
c  custom
p plain text sql
"""
import argparse
from datetime import datetime as dt
import json
import os
from typing import Union
from pathlib import Path
import sys
from sqlalchemy import create_engine
try:
    from mdr import appconfig as ac
except ImportError:
    import appconfig as ac

try:
    from mdr import hashing as hs
except ImportError:
    import hashing as hs


def nowstr():
    return dt.now().strftime('%Y-%m-%d %H:%M:%S')


def get_file_name(db_name):
    return f'{db_name}.backup'


def get_default_bkp_name():
    return dt.now().strftime('%Y%m%d')


def compose_bkp_file_path(*, backup_path,  backup_name, db_name,  file_name):
    return backup_path/ backup_path/ backup_name / db_name / file_name


def hash_dump(bkp_path):
    data = hs.createHashtree(bkp_path)
    if type(bkp_path) is str:
        bkp_path = Path(bkp_path)
    file_path = bkp_path / 'hash_tree.json'
    print(json.dumps({
        'dt': nowstr(),
        'msg': f'creating hash_tree at {str(file_path)}'
    }))
    if 'hash_tree.json' in data:
        data.pop('hash_tree.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, sort_keys=True, indent=4)


def get_schema_list(
        db: ac.PostgresConfig,
        db_name: str
):
    sql = '''
    SELECT schema_name
    FROM  information_schema.schemata
    WHERE schema_name <> 'information_schema'
        AND schema_name <> 'public'
        AND schema_name NOT LIKE 'pg%%'
    ORDER BY schema_name;
    '''
    uri = db.get_uri(db_name)
    engine = create_engine(uri)
    with engine.connect() as con:
        data = con.execute(sql).fetchall()
    engine.dispose()
    schema_list = [elm[0] for elm in data]
    schema_list = ['public'] + schema_list
    return schema_list


def _dump_cmd_template(db: ac.PostgresConfig, db_name, file_path, bkp_name, caller, schema=None):
    """Reference: https://www.postgresql.org/docs/10/app-pgdump.html"""
    core_cmd_fragments = [
        f'{db.pg_dump_path}',
        '--file', f'\'{file_path.__str__()}\'',
        '--host', f'\'{db.host}\'',
        '--port', f'\'{db.port}\'',
        '--username', f'\'{db.user}\'',
        '--no-password',
        '--verbose',
        '--format=c',
        '--no-owner',
        '--section=pre-data',
        '--section=data',
        '--section=post-data',
        '--no-privileges',
        '--no-tablespaces',
        '--no-unlogged-table-data',
    ]
    if schema:
        core_cmd_fragments += ['--schema', f'\'{schema}\'']
    core_cmd_fragments += [f'\'{db_name}\'']
    core_cmd = ' '.join(core_cmd_fragments)
    log_cmd_fragments = ['>>', f'logs/{bkp_name}_{caller}.log', '2>&1']
    cmd = ' '.join([core_cmd] + log_cmd_fragments)
    return cmd


def execute_cmd(cmd, db_name, *, armed=False, file_path: Union[str, Path] = None):
    if not armed:
        print(cmd)
    else:
        print(
            json.dumps({
                'dt': nowstr(),
                'msg': f'dumping {db_name} to {str(file_path)}'
            })
        )
        os.system(cmd)
        print(
            json.dumps({
                'dt': nowstr(),
                'msg': f'finished dumping {db_name} to {str(file_path)}'
            })
        )


def basic_dump(
    db: ac.PostgresConfig,
    bkp_base_path: Path,
    db_name: str,
    armed=False
):
    """
    dump the complete database into one ugly big file
    Reference: https://www.postgresql.org/docs/10/app-pgdump.html
    """
    bkp_name = (dt.now()).strftime('%Y%m%d')
    bkp_path = bkp_base_path / f'{bkp_name}'
    file_name = f'{db_name}.backup'
    file_path = bkp_path / db_name / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    template_config = {
        'db': db,
        'db_name': db_name,
        'file_path': file_path,
        'bkp_name': bkp_name,
        'caller': 'multi_dump'
    }
    cmd = _dump_cmd_template(**template_config)
    execute_cmd(cmd, db_name, armed=armed, file_path=file_path)
    if armed:
        hash_dump(bkp_path)


def schema_dump_loop(
        db: ac.PostgresConfig,
        bkp_base_path: Path,
        schema_list: [],
        db_name: str,
        armed=False
):
    """ Reference: https://www.postgresql.org/docs/10/app-pgdump.html """
    bkp_name = dt.now().strftime('%Y%m%d')
    bkp_path = bkp_base_path / f'{bkp_name}'
    for schema in schema_list:
        file_name = f'{schema}.backup'
        file_path = bkp_path / db_name / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        template_config = {
            'db': db,
            'db_name': db_name,
            'file_path': file_path,
            'bkp_name': bkp_name,
            'caller': 'multi_dump',
            'schema': schema
        }
        cmd = _dump_cmd_template(**template_config)
        execute_cmd(cmd, db_name, armed=armed, file_path=file_path)
    if armed:
        hash_dump(bkp_path)


def main(args: argparse.Namespace):
    if sys.platform != 'linux':
        raise NotImplementedError('script is only configured to work on linux')
    Path('logs').mkdir(exist_ok=True, parents=True)
    bkp_base_path = Path(args.bkp_base_path)
    if args.dump_type == 'schema_wise':
        schema_list = get_schema_list(ac.pgc, args.db_name)
        schema_dump_loop(ac.pgc, bkp_base_path, schema_list, args.db_name, args.armed)
    elif args.dump_type == 'basic':
        basic_dump(ac.pgc, bkp_base_path, args.db_name, args.armed)
    else:
        msg = 'only `basic` or `schema_wise` dump implemented'
        raise NotImplementedError(msg)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument(
        'db_name',
        help='name of database to dump'
    )
    p.add_argument(
        'dump_type',
        help='backup each schema in a separate file or the complete database in one single file',
        choices=['schema_wise', 'basic']
    )
    p.add_argument(
        '--bkp_base_path',
        default=str(ac.BKP_BASE_PATH),
        help='path to ALL backups e.g. /home/user/db/bkp'
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
    ac.check_if_known_db_name(a.db_name)
    main(a)

