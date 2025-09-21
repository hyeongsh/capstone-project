from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv() # .env 파일 읽어오기

db_pool = pool.SimpleConnectionPool(
	minconn=1,
	maxconn=10,
	dbname=os.getenv("PGDATABASE"),
	user=os.getenv("PGUSER"),
	password=os.getenv("PGPASSWORD"),
	host=os.getenv("PGHOST"),
	port=os.getenv("PGPORT")
)