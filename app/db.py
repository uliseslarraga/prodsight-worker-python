import psycopg
from psycopg.rows import dict_row
from .config import settings

def get_conn():
    return psycopg.connect(settings.db_dsn, row_factory=dict_row)
