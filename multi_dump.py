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
from pathlib import Path
import sys
from sqlalchemy import create_engine
from appconfig import PostgresConfig, pgc, USER, check_if_known_db_name


def nowstr():
    return dt.now().strftime('%Y-%m-%d %H:%M:%S')


def get_schema_list(
        db: PostgresConfig,
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


def basic_dump(
    db: PostgresConfig,
    backup_path: Path,
    db_name: str,
    armed=False
):
    """
    dump the complete database into one ugly big file
    Reference: https://www.postgresql.org/docs/10/app-pgdump.html
    """
    backup_name = (dt.now()).strftime('%Y%m%d')
    file_name = f'{db_name}.backup'
    file_path = backup_path / f'{backup_name}' / db_name / file_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = (
        f"{db.pg_dump_path}  --file '{file_path.__str__()}' "
        f" --host '{db.host}' "
        f" --port '{db.port}' "
        f" --username '{db.user}' "
        f" --no-password "
        f" --verbose "
        f" --format=c "
        f" --no-owner "
        f" --section=pre-data "
        f" --section=data "
        f" --section=post-data "
        f" --no-privileges "
        f" --no-tablespaces "
        f" --no-unlogged-table-data "
        f" '{db_name}' "
        f" >> logs/{backup_name}_multidump.log 2>&1 "
    )
    if armed:
        print(
            json.dumps({
                'dt': nowstr(),
                'msg': f'dumping {db_name} to {file_path.__str__()}'
            })
        )
        os.system(cmd)
        print(
            json.dumps({
                'dt': nowstr(),
                'msg': f'finished dumping {db_name} to {file_path.__str__()}'
            })
        )
    else:
        print(cmd)


def schema_dump_loop(
        db: PostgresConfig,
        bkp_path: Path,
        schema_list: [],
        db_name: str,
        armed=False
):
    """ Reference: https://www.postgresql.org/docs/10/app-pgdump.html """
    backup_name = dt.now().strftime('%Y%m%d')
    for schema in schema_list:
        file_name = f'{schema}.backup'
        file_path = bkp_path / f'{backup_name}' / db_name / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = (
            f"{db.pg_dump_path}  --file '{file_path.__str__()}' "
            f" --host '{db.host}' "
            f" --port '{db.port}' "
            f" --username '{db.user}' "
            f" --no-password "
            f" --verbose "
            f" --format=c "
            f" --no-owner "
            f" --section=pre-data "
            f" --section=data "
            f" --section=post-data "
            f" --no-privileges "
            f" --no-tablespaces "
            f" --no-unlogged-table-data "
            f" --schema '{schema}' "
            f" '{db_name}' "
            f" >> logs/{backup_name}_multi_dump.log 2>&1 "
        )
        if armed:
            print(
                json.dumps({
                    'dt': nowstr(),
                    'msg': f'dumping {schema} to {file_path.__str__()}'
                })
            )
            os.system(cmd)
            print(
                json.dumps({
                    'dt': nowstr(),
                    'msg': f'dumped {schema} to {file_path.__str__()}'
                })
            )
        else:
            print(cmd)


def main(args: argparse.Namespace):
    if sys.platform != 'linux':
        raise NotImplementedError('script is only configured to work on linux')
    Path('logs').mkdir(exist_ok=True, parents=True)
    backup_path = Path(args.backup_path)
    if args.dump_type == 'schema_wise':
        schema_list = get_schema_list(pgc, args.db_name)
        schema_dump_loop(pgc, backup_path, schema_list, args.db_name, args.armed)
    elif args.dump_type == 'basic':
        basic_dump(pgc, backup_path, args.db_name, args.armed)
    else:
        msg = 'only `basic` or `schema_wise` dump implemented'
        raise NotImplementedError(msg)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        'backup_path',
        default=f'/home/{USER}/db/bkp',
        help='path to ALL backups e.g. /home/user/db/bkp')
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
    check_if_known_db_name(a.db_name)
    main(a)
