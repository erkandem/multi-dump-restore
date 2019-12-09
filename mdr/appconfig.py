import os
import getpass
from pathlib import Path
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv(raise_error_if_not_found=True))


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
BKP_BASE_PATH = os.getenv('BKP_BASE_PATH') or f'/home/{USER}/db/bkp'
BKP_BASE_PATH = Path(BKP_BASE_PATH)

KNOWN_DB_NAMES = [
    # previously configured and used databases
    # manually maintained because the script
    # won't touch ~/.pgpass
]


def check_if_known_db_name(db_name):
    if db_name not in KNOWN_DB_NAMES:
        print(
            f'The backup_db_name given ({db_name}) '
            f'does not appear in the known_databases list in `appconfig`'
            f'Be sure you left a record in the `.pgpass` file'
        )
