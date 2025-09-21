from psycopg2.extensions import connection
from config import db_pool
from repository.interface.label_aliases_repository import LabelAliasesRepository

class LabelAliasesRepositoryImpl(LabelAliasesRepository):
	def __init__(self):
		self.db_pool = db_pool

	def get_object_id_by_alias(self, alias):
		conn: connection = self.db_pool.getconn()
		cur = conn.cursor()
		try:
			cur.execute(
				"SELECT object_id FROM label_aliases WHERE alias = %s", (alias,)
			)
			return cur.fetchone()
		finally:
			cur.close()
			self.db_pool.putconn(conn)