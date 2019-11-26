import multi_dump as md
from pathlib import Path
from datetime import datetime as dt


def test_get_file_name():
    db_name = 'kikeriki'
    assert f'{db_name}.backup' == md.get_file_name(db_name)


def test_get_default_bkp_name():
    assert dt.now().strftime('%Y%m%d') == md.get_default_bkp_name()


def test_compose_bkp_file_path():
    c = {
        'backup_path': Path('/somewhere'),
        'backup_name': 'some_name',
        'db_name': 'some_db',
        'file_name': 'some_file.backup'
    }
    expected = c['backup_path'] / c['backup_path'] / c['backup_name'] / c['db_name'] / c['file_name']
    assert expected == md.compose_bkp_file_path(**c)
