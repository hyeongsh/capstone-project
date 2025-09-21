from abc import ABC, abstractmethod

class ObjectsRepository(ABC):
	
	@abstractmethod
	def get_name_by_id(self, id: int) -> str | None:
		pass

	@abstractmethod
	def find_by_id(self, id: int) -> tuple | None:
		pass

	@abstractmethod
	def find_by_name(self, name: str) -> tuple | None:
		pass
