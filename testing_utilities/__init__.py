import string
from datetime import datetime as dt
import tempfile
import pandas as pd
import numpy as np
from sqlalchemy import Date, Float
from sqlalchemy import create_engine
from pathlib import Path
import appconfig
from sqlalchemy.engine import Engine
from pandas.core.indexes.datetimes import DatetimeIndex

TESTING_DATABASE = 'mdr'


class SampleData:
    schema_names = [
        'ultra_fancy',
        'super_fancy',
        'normal_fancy',
        'minor_fancy',
        'not_fancy'
    ]
    table_names = [f'hannibal_{c}' for c in string.ascii_lowercase[0:1]]
    bdays = DatetimeIndex
    df_data = {
            'dt': '',
            'x': '',
            'y': '',
            'z': '',
            'xx': '',
            'yy': '',
            'zz': '',
            'xy': '',
            'xz': '',
            'yz': '',
            'xxx': '',
            'yyy': '',
            'zzz': '',
            'xxy': '',
            'xxz': '',
            'yyx': '',
            'yyz': '',
            'zzx': '',
            'zzy': ''
        }
    df: pd.DataFrame
    dtypes = {c: Date if c == 'dt' else Float for c in list(df_data)}

    def __init__(self):
        bdays = pd.date_range(start=dt(2019, 1, 1), end=dt(2019, 12, 31))
        self.bdays = bdays
        self.df = pd.DataFrame({
            'dt': bdays,
            'x': np.random.rand(len(bdays)),
            'y': np.random.rand(len(bdays)),
            'z': np.random.rand(len(bdays)),
            'xx': np.random.rand(len(bdays)),
            'yy': np.random.rand(len(bdays)),
            'zz': np.random.rand(len(bdays)),
            'xy': np.random.rand(len(bdays)),
            'xz': np.random.rand(len(bdays)),
            'yz': np.random.rand(len(bdays)),
            'xxx': np.random.rand(len(bdays)),
            'yyy': np.random.rand(len(bdays)),
            'zzz': np.random.rand(len(bdays)),
            'xxy': np.random.rand(len(bdays)),
            'xxz': np.random.rand(len(bdays)),
            'yyx': np.random.rand(len(bdays)),
            'yyz': np.random.rand(len(bdays)),
            'zzx': np.random.rand(len(bdays)),
            'zzy': np.random.rand(len(bdays))
        })


class PostgresTestingSuit:
    testing_pgc_data = {
        'user': 'postgres',
        'pw': 'postgres',
        'host': 'localhost',
        'port': '5433',
        'driver': 'psycopg2',
        'db': 'postgresql'
    }
    engine: Engine

    def __init__(self):
        self.testing_pgc = appconfig.PostgresConfig()
        self.testing_pgc.__dict__.update(self.testing_pgc_data)
        self.uri = self.testing_pgc.get_uri(TESTING_DATABASE)
        self.engine = create_engine(self.uri)

    @staticmethod
    def get_and_patch_temporary_bkp_dir():
        temp_dir = Path(tempfile.TemporaryDirectory().name)
        testing_bkp_base_path = temp_dir / 'db' / 'bkp'
        appconfig.BKP_BASE_PATH = testing_bkp_base_path

    @staticmethod
    def create_table_sql(schema, table):
        return f'''
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            dt date,
            x double precision,
            y double precision,
            z double precision,
            xx double precision,
            yy double precision,
            zz double precision,
            xy double precision,
            xz double precision,
            yz double precision,
            xxx double precision,
            yyy double precision,
            zzz double precision,
            xxy double precision,
            xxz double precision,
            yyx double precision,
            yyz double precision,
            zzx double precision,
            zzy double precision,
            PRIMARY KEY (dt)
        );
        '''

    @staticmethod
    def create_schemata(schema, engine):
        with engine.connect() as con:
            con.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')

    @staticmethod
    def drop_schema(schema, engine):
        con = engine.raw_connection()
        cursor = con.cursor()
        cursor.execute(f'DROP SCHEMA {schema} CASCADE;')
        con.commit()
        cursor.close()
        con.close()

    @staticmethod
    def create_table(schema, table, engine):
        with engine.connect() as con:
            sql = PostgresTestingSuit.create_table_sql(schema, table)
            con.execute(sql)

    def init_db(self):
        sd = SampleData()
        for schema in sd.schema_names:
            self.create_schemata(schema, self.engine)
            for table in sd.table_names:
                self.create_table(schema, table, self.engine)
                sd.df.to_sql(
                    name=table,
                    schema=schema,
                    con=self.engine,
                    dtype=sd.dtypes,
                    index=False,
                    if_exists='replace'
                )

    def del_db(self):
        for schema in SampleData.schema_names:
            self.drop_schema(schema, self.engine)


pgts = PostgresTestingSuit()
