from psycopg2.extensions import connection
from config import db_pool
from repository.interface.objects_repository import ObjectsRepository

class ObjectsRepositoryImpl(ObjectsRepository):
	def __init__(self):
		self.db_pool = db_pool

	def get_name_by_id(self, id):
		conn: connection = self.db_pool.getconn()
		cur = conn.cursor()
		try:
			cur.execute(
				"SELECT name FROM objects WHERE object_id = %s", (id,)
			)
			result = cur.fetchone()
			if result:
				return result[0]
			return result
		finally:
			cur.close()
			self.db_pool.putconn(conn)

	def find_by_id(self, id):
		conn: connection = self.db_pool.getconn()
		cur = conn.cursor()
		try:
			cur.execute(
				"SELECT * FROM objects WHERE object_id = %s", (id,)
			)
			return cur.fetchone()
		finally:
			cur.close()
			self.db_pool.putconn(conn)
	
	def find_by_name(self, name):
		conn: connection = self.db_pool.getconn()
		cur = conn.cursor()
		try:
			cur.execute(
				"SELECT * FROM objects WHERE name = %s", (name,)
			)
			return cur.fetchone()
		finally:
			cur.close()
			self.db_pool.putconn(conn)