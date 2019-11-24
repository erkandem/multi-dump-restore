import os
import getpass
import dotenv
dotenv.load_dotenv('.env')


class PostgresConfig:
    def __init__(self):
        self.user = os.getenv('PG_USER')
        self.pw = os.getenv('PG_PW')
        self.host = os.getenv('PG_HOST')
        self.port = os.getenv('PG_PORT')
        self.driver = 'psycopg2'
        self.db = 'postgresql'
        self.pg_dump_path = 'pg_dump'
        self.pg_restore_path = 'pg_restore'
    
    def get_uri(self, db_name):
        return f"{self.db}+{self.driver}://{self.user}:{self.pw}@{self.host}:{self.port}/{db_name}"


pgc = PostgresConfig()
USER = getpass.getuser()

known_db_names = [
    # previously configured and used databases ~/.pgpass
    'experimental_usyh_rawdata',
    'options_rawdata',
    'pymarkets_tests_db_two',
    'pymarkets_tests_db_two',
    'prices_intraday',
    'pgivbase'
]
